ARDUINO_IP = "172.19.15.213"
ARDUINO_PORT = 4210

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

N_STEPS = 10               # number of steps to reach target position (resolution per finger: 0->9)
EMA_ALPHA = 0.4            # smoothing factor (lower = smoother but more lag)

FINGER_OPEN_ANGLE = 150.0  # angle (in degrees) at which we consider a finger fully open
FINGER_CLOSED_ANGLE = 45.0 # angle (in degrees) at which we consider a finger fully closed

THUMB_OPEN = 165.0         # normalized tip-to-index-knuckle distance, thumb out   (after calibration)
THUMB_CLOSED = 120.0       # normalized tip-to-index-knuckle distance, thumb in  (after calibration)

DEBUG = False              # set to True to print debug info about angles and distances for each finger

MODEL_PATH = './hand_landmarker.task'