# imports
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import serial

# serial setup
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Update with your serial port and baud rate

# Hand landmark connections (MediaPipe hand has 21 landmarks)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (5, 9), (9, 13), (13, 17),  # Knuckle connections
]
 # tios and pips for Index, Middle, Ring and Pinky fingers
TIPS = [8, 12, 16, 20]
PIPS = [6, 10, 14, 18]

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
last_binary_state = "00000"  # all fingers folded

# create a hand landmarker instance with the livestream mode
def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    #print(f'hand landmarker result: {result}')
    global last_binary_state, latest_image

    # capture the image for the main thread to display
    latest_image = output_image.numpy_view()
    latest_image = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)
    # Get the frame from output_image and draw landmarks
    #image_data = output_image.numpy_view()
    #image_data = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
    
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
    
        # process the first detected hand
        landmarks = result.hand_landmarks[0]
        binary_state = ""

        # FINGER LOGIC
        # points: Index(8, 6), Middle(12, 10), Ring(16, 14), Pinky(20, 18)
        for tip, pip in zip(TIPS, PIPS):
            if landmarks[tip].y < landmarks[pip].y: # if tip is above pip, finger is open
                binary_state += "1"
            else:                                   # if tip is below pip, finger is closed
                binary_state += "0"

        # Thumb logic: if the thumb pip is to the right of the thumb mcp, then thumb is closed
        if landmarks[4].x < landmarks[3].x:
            binary_state += "0" # folded
        else:
            binary_state += "1" # open
    
        # SERIAL COMMS LOGIC
        if binary_state != last_binary_state:
            ser.write(binary_state.encode())  # Send the binary state as bytes to the MCU
            print(f"Sending to MCU: {binary_state}")
            last_binary_state = binary_state


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