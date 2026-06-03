# imports
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import serial
import numpy as np
import socket

# IP Configuration for Arduino
ARDUINO_IP = "172.19.4.36"
ARDUINO_PORT = 4210

sock = socket.socket(socket.AF_NET, socket.SOCK_DGRAM)

# serial setup
#ser = serial.Serial('/dev/ttyUSB0', 9600)  # Update with your serial port and baud rate


# Hand landmark connections (MediaPipe hand has 21 landmarks)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (5, 9), (9, 13), (13, 17),  # Knuckle connections
]
 # tips and pips for Index, Middle, Ring and Pinky fingers
TIPS = [8, 12, 16, 20]
PIPS = [6, 10, 14, 18]

# (MCP, PIP, TIP) for index, middle, ring and pinky fingers
# used for joint-angle flexion logic
FINGER_JOINTS = [(5, 6, 8), (9, 10, 12), (13, 14, 16), (17, 18, 20)]

# tunable configuration
N_STEPS = 10               # number of steps to reach target position (resolution per finger: 0->9)
EMA_ALPHA = 0.4            # smoothing factor (lower = smoother but more lag)

FINGER_OPEN_ANGLE = 150.0  # angle (in degrees) at which we consider a finger fully open
FINGER_CLOSED_ANGLE = 45.0 # angle (in degrees) at which we consider a finger fully closed

THUMB_OPEN = 0.65          # normalized tip-to-index-knuckle distance, thumb out   (after calibration)
THUMB_CLOSED = 0.25         # normalized tip-to-index-knuckle distance, thumb in  (after calibration)

DEBUG = False              # set to True to print debug info about angles and distances for each finger

# model
model_path = './hand_landmarker.task'

# creating the task
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# global variables for thread communication
latest_image = None
smoothed = [0.0] * 5         # smoothed values for each finger (4 fingers + thumb) 
last_sent_state = None          # last sent state to the MCU 


def _pt(landmarks, i):
    return np.array([landmarks[i].x, landmarks[i].y, landmarks[i].z])

def joint_angle(landmarks, a, b, c):
    """Angle (deg) at vertex b for the a-b-c chain, ~180 = straight, small = curled"""
    v1 = _pt(landmarks, a) - _pt(landmarks, b)
    v2 = _pt(landmarks, c) - _pt(landmarks, b)
    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def norm_dist(landmarks, a, b, r1, r2):
    """Distance a-b normalized by reference length r1-r2 (scale-invariant)"""
    d = np.linalg.norm(_pt(landmarks,a) - _pt(landmarks, b))
    ref = np.linalg.norm(_pt(landmarks, r1) - _pt(landmarks, r2)) + 1e-6
    return d / ref 
    
def remap01(value, lo, hi):
    """Map value from [lo, hi] to [0, 1], clamped"""
    return max(0.0, min(1.0, (value - lo) / (hi - lo + 1e-6)))

# create a hand landmarker instance with the livestream mode
def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    #print(f'hand landmarker result: {result}')
    global last_sent_state, latest_image, smoothed

    # capture the image for the main thread to display
    latest_image = output_image.numpy_view()
    latest_image = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)
    # Get the frame from output_image and draw landmarks
    #image_data = output_image.numpy_view()
    #image_data = cv2.cvtColor(image_data, (landmarks,cv2.COLOR_RGB2BGR)
    
    if not result.hand_landmarks:
        return

    # Draw landmarks on the image
    if result.hand_landmarks:
        h, w, c = latest_image.shape
        for hand_landmarks in result.hand_landmarks:
            # Draw each landmark point
            for landmark in hand_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                # Draw circle at each landmark point
                cv2.circle(latest_image, (x, y), 3, (0, 255, 0), -1)
            
            # Draw connections between landmarks (fingers)
            for connection in HAND_CONNECTIONS:
                start_idx = connection[0]
                end_idx = connection[1]
                start_landmark = hand_landmarks[start_idx]
                end_landmark = hand_landmarks[end_idx]
                start_point = (int(start_landmark.x * w), int(start_landmark.y * h))
                end_point = (int(end_landmark.x * w), int(end_landmark.y * h))
                cv2.line(latest_image, start_point, end_point, (255, 0, 0), 2)
    
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
        thumb = norm_dist(world, 4, 5, 0, 9) # thumb tip to index knuckle, normalized by wrist-to-index-knuckle
        raw.append(remap01(thumb, THUMB_CLOSED, THUMB_OPEN))

        # smooth EMA (Exponential Moving Average) then quantize into steps
        steps = []
        for i in range(5):
            smoothed[i] = EMA_ALPHA * raw[i] +(1.0 - EMA_ALPHA) * smoothed[i]
            steps.append(round(smoothed[i] * (N_STEPS - 1)))

        state = ''.join(str(s) for s in steps)  # for instance, "90743" (index -> thumb)

        if DEBUG:
            print(f"Raw: {[round(r,2) for r in raw]}, Smoothed: {[round(s,2) for s in smoothed]}, Steps: {steps}")
        
        # # send only if state changed (to reduce serial noise)
        # if state != last_sent_state:
        #     ser.write((state + '\n').encode())
        #     print(f"Sending to MCU: {state}")
        #     last_sent_state = state

        sock.sendto((state + '\n').encode(), (ARDUINO_IP, ARDUINO_PORT))

options = HandLandmarkerOptions(
    base_options = BaseOptions(model_asset_path=model_path),
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