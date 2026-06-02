# main.py
import time
import cv2
import mediapipe as mp
import os

import config
from serial_io import SerialSender
from control import (
    AngleController, angle_deg,
    openness_from_angle, openness_to_servo
)
from macro import MacroRecorder, MacroPlayer
from game_rps import RPSGame
from ui import draw_overlay
from vision import HandVision

latest_image = None
latest_landmarks = None  # keep last landmarks for debugging if needed

# App state
mode = "LIVE"  # LIVE or GAME

# Create modules
sender = SerialSender(config.SERIAL_PORT, config.BAUD_RATE)

controller = AngleController(
    servo_mins=config.SERVO_MINS,
    servo_maxs=config.SERVO_MAXS,
    alpha=config.ALPHA,
    deadband_deg=config.DEADBAND_DEG,
    max_step_deg=config.MAX_STEP_DEG,
    send_hz=config.SEND_HZ,
)

rec = MacroRecorder()
player = MacroPlayer(play_hz=config.PLAY_HZ)

rps = RPSGame(
    servo_mins=config.SERVO_MINS,
    servo_maxs=config.SERVO_MAXS,
    shake_window=config.SHAKE_WINDOW,
    shake_threshold=config.SHAKE_THRESHOLD,
    cooldown_s=config.SHAKE_COOLDOWN_S,
)

def send_if_due(angles):
    # controller.should_send updates controller.last_sent and timing
    if controller.should_send(angles):
        sender.send_angles(angles)
        return True
    return False

def compute_live_targets(landmarks):
    # Index finger angle: 5-6-8 (MCP-PIP-TIP)
    idx_angle = angle_deg(landmarks[5], landmarks[6], landmarks[8])
    mid_angle = angle_deg(landmarks[9], landmarks[10], landmarks[12])
    rng_angle = angle_deg(landmarks[13], landmarks[14], landmarks[16])
    lit_angle = angle_deg(landmarks[17], landmarks[18], landmarks[20])

    idx_open = openness_from_angle(idx_angle, config.CLOSED_ANGLE, config.OPEN_ANGLE)
    mid_open = openness_from_angle(mid_angle, config.CLOSED_ANGLE, config.OPEN_ANGLE)
    rng_open = openness_from_angle(rng_angle, config.CLOSED_ANGLE, config.OPEN_ANGLE)
    lit_open = openness_from_angle(lit_angle, config.CLOSED_ANGLE, config.OPEN_ANGLE)

    # Thumb: 2-3-4
    thm_angle = angle_deg(landmarks[2], landmarks[3], landmarks[4])
    thm_open = openness_from_angle(thm_angle, config.CLOSED_ANGLE, config.OPEN_ANGLE)

    mins = config.SERVO_MINS
    maxs = config.SERVO_MAXS

    targets = [
        openness_to_servo(idx_open, mins[0], maxs[0]),
        openness_to_servo(mid_open, mins[1], maxs[1]),
        openness_to_servo(rng_open, mins[2], maxs[2]),
        openness_to_servo(lit_open, mins[3], maxs[3]),
        openness_to_servo(thm_open, mins[4], maxs[4]),
    ]
    return targets

def mp_callback(result, output_image: mp.Image, timestamp_ms: int):
    global latest_image, latest_landmarks, mode

    # latest frame for UI
    latest_image = output_image.numpy_view()
    latest_image = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)

    if not result.hand_landmarks:
        return

    landmarks = result.hand_landmarks[0]
    latest_landmarks = landmarks

    # 1) Playback overrides everything
    angles_from_player = player.get_target_angles()
    if angles_from_player is not None:
        send_if_due(angles_from_player)
        rec.update(angles_from_player)
        return

    # 2) GAME mode: shake triggers RPS pose
    if mode == "GAME":
        pose = rps.update(landmarks)
        if pose is not None:
            send_if_due(pose)
            rec.update(pose)
        return

    # 3) LIVE continuous motion
    targets = compute_live_targets(landmarks)
    smooth_angles = controller.smooth_targets(targets)
    send_if_due(smooth_angles)
    rec.update(smooth_angles)

def main():
    global mode

    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    with HandVision(config.MODEL_PATH, mp_callback) as hv:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ts_ms = int(time.time() * 1000)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            hv.detect_async(mp_image, ts_ms)

            if latest_image is not None:
                draw_overlay(latest_image, mode, controller.last_sent, rec, player, rps)
                cv2.imshow("Robot Hand Control", latest_image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('g'):
                mode = "GAME" if mode == "LIVE" else "LIVE"
                rps.reset()

            elif key == ord('r'):
                rec.start(duration_s=config.MACRO_DURATION_S)

            elif key == ord('p'):
                if rec.frames:
                    rec.save_csv(config.LAST_MACRO_PATH)
                if os.path.exists(config.LAST_MACRO_PATH):
                    player.load_csv(config.LAST_MACRO_PATH)
                    player.start(loop=False)

            elif key == ord('s'):
                player.stop()

            elif key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()