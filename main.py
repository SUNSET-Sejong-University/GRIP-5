# imports
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import serial
import numpy as np
import socket
import argparse
from gesture_logic import *
from config import *
import drawing
from transport import make_transport

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    "--mode",
    type=str,
    default="wireless",
    help="Should be either 'wireless' or 'serial'",
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


# create a hand landmarker instance with the livestream mode
def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    #print(f'hand landmarker result: {result}')
    global last_sent_state, latest_image, smoothed

    # capture the image for the main thread to display
    latest_image = output_image.numpy_view()
    latest_image = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)

    if not result.hand_landmarks:
        return

    # Draw landmarks on the image
    if result.hand_landmarks:
        drawing.draw_landmarks(latest_image, result.hand_landmarks, HAND_CONNECTIONS)
      
        # continuous flexion for the first detected hand
        # 2D image landmarks: used only for drawing (above)
        # 3D world landmarks: used for orientation-independent joint angles
        if not result.hand_world_landmarks:
            return
        world = result.hand_world_landmarks[0]

        raw = []
        for mcp, pip, tip in FINGER_JOINTS:
            angle = joint_angle(world, mcp, pip, tip)
            raw.append(remap01(angle, FINGER_CLOSED_ANGLE, FINGER_OPEN_ANGLE))
        # thumb logic: thumb tip to index knuckle distance, normalized by wrist-to-index-knuckle distance (to be scale invariant), empirically tuned
        thumb = joint_angle(world, 2, 3, 4) # thumb tip to index knuckle, normalized by wrist-to-index-knuckle
        raw.append(remap01(thumb, THUMB_CLOSED, THUMB_OPEN))

        # smooth EMA (Exponential Moving Average) then quantize into steps
        steps = []
        for i in range(5):
            smoothed[i] = EMA_ALPHA * raw[i] +(1.0 - EMA_ALPHA) * smoothed[i]
            steps.append(round(smoothed[i] * (N_STEPS - 1)))

        state = ''.join(str(s) for s in steps)  # for instance, "90743" (index -> thumb)

        if DEBUG:
            print(f"Raw: {[round(r,2) for r in raw]}, Smoothed: {[round(s,2) for s in smoothed]}, Steps: {steps}")
        
        transport.send(state)

options = HandLandmarkerOptions(
    base_options = BaseOptions(model_asset_path=MODEL_PATH),
    running_mode = VisionRunningMode.LIVE_STREAM,
    result_callback = print_result
)
with HandLandmarker.create_from_options(options) as landmarker:
    # landmarker is used here
    # use opencv's VideoCapture to read from webcam
    #create a loop to read the latest frame fom the webcam using VideoCapture
    cap = cv2.VideoCapture(0)
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
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Clean up
cap.release()
cv2.destroyAllWindows()