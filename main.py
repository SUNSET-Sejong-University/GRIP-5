# imports
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import argparse
import gesture_logic
import config
import drawing
from transport import make_transport
import rps

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    "--mode",
    type=str,
    default="wireless",
    help="Should be either 'wireless' or 'serial'",
)

parser.add_argument(
    "--game",
    action="store_true",
    help="Enables Rock-Paper-Scissor game mode (rounds auto-play)"
)
args = parser.parse_args()

transport = make_transport(args.mode, ip=config.ARDUINO_IP, port=config.ARDUINO_PORT)

# creating the task
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# global variables for thread communication
latest_image = None
smoothed = [0.0] * 5         # smoothed values for each finger (4 fingers + thumb) 
last_sent_state = None       # last sent state to the MCU 

game = rps.RPSGame()         # for game mode, set cheat=True for an unbeatable hand
game.active = args.game      # game mode is set once, from the flag

# create a hand landmarker instance with the livestream mode
def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    #print(f'hand landmarker result: {result}')
    global last_sent_state, latest_image, smoothed

    # capture the image for the main thread to display
    latest_image = output_image.numpy_view()
    latest_image = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)

    steps = None  # stays None if no usable hand this frame

    if not result.hand_landmarks:
        return

    # Draw landmarks on the image
    if result.hand_landmarks:
        drawing.draw_landmarks(latest_image, result.hand_landmarks, config.HAND_CONNECTIONS)
      
        # continuous flexion for the first detected hand
        # 2D image landmarks: used only for drawing (above)
        # 3D world landmarks: used for orientation-independent joint angles
        if not result.hand_world_landmarks:
            return
        world = result.hand_world_landmarks[0]

        raw = []
        for mcp, pip, tip in config.FINGER_JOINTS:
            angle = gesture_logic.joint_angle(world, mcp, pip, tip)
            raw.append(gesture_logic.remap01(angle, config.FINGER_CLOSED_ANGLE, config.FINGER_OPEN_ANGLE))
        # thumb logic: thumb tip to index knuckle distance, normalized by wrist-to-index-knuckle distance (to be scale invariant), empirically tuned
        thumb = gesture_logic.joint_angle(world, 2, 3, 4) # thumb tip to index knuckle, normalized by wrist-to-index-knuckle
        raw.append(gesture_logic.remap01(thumb, config.THUMB_CLOSED, config.THUMB_OPEN))

        # smooth EMA (Exponential Moving Average) then quantize into steps
        steps = []
        for i in range(5):
            smoothed[i] = config.EMA_ALPHA * raw[i] +(1.0 - config.EMA_ALPHA) * smoothed[i]
            steps.append(round(smoothed[i] * (config.N_STEPS - 1)))

        #state = ''.join(str(s) for s in steps)  # for instance, "90743" (index -> thumb)

        if config.DEBUG:
            print(f"Raw: {[round(r,2) for r in raw]}, Smoothed: {[round(s,2) for s in smoothed]}, Steps: {steps}")
        
    # decide what to send
    if game.active:
        to_send = game.update(steps)
        if to_send is not None:
            transport.send(to_send)
        game.draw_overlay(latest_image)
    elif steps is not None:
        state = ''.join(str(s) for s in steps)    # for instance, "90743" (index -> thumb)
        transport.send(state)

options = HandLandmarkerOptions(
    base_options = BaseOptions(model_asset_path=config.MODEL_PATH),
    running_mode = VisionRunningMode.LIVE_STREAM,
    result_callback = print_result
)
with HandLandmarker.create_from_options(options) as landmarker:
    # landmarker is used here
    # use opencv's VideoCapture to read from webcam
    #create a loop to read the latest frame fom the webcam using VideoCapture
    cap = cv2.VideoCapture(0)
    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty frame...")
                continue

            # convert the frame to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # get the current timestamp in milliseconds
            frame_timestamp_ms = int(time.time() * 1000)
            
            # create a mp.Image from the numpy array
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            landmarker.detect_async(mp_image, frame_timestamp_ms)

            #draw/show if we have a frame (handles threading safely)
            if latest_image is not None:
                cv2.imshow('Robot Hand Control', latest_image)
            
            # Press 'q' to exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        transport.close()