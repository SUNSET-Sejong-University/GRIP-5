# config.py
# Centralized configuration constants.

# Serial
SERIAL_PORT = "COM9"
BAUD_RATE = 9600

# Model
MODEL_PATH = "./hand_landmarker.task"
CAMERA_INDEX = 0

# Servo ranges (order: index, middle, ring, little, thumb)
IDX_MIN, IDX_MAX = 45, 150
MID_MIN, MID_MAX = 45, 150
RNG_MIN, RNG_MAX = 45, 150
LIT_MIN, LIT_MAX = 45, 150
THM_MIN, THM_MAX = 45, 150

SERVO_MINS = [IDX_MIN, MID_MIN, RNG_MIN, LIT_MIN, THM_MIN]
SERVO_MAXS = [IDX_MAX, MID_MAX, RNG_MAX, LIT_MAX, THM_MAX]

# Continuous openness mapping (joint angle -> openness)
OPEN_ANGLE = 175.0
CLOSED_ANGLE = 95.0

# Filtering / control
ALPHA = 0.25          # EMA smoothing
DEADBAND_DEG = 2      # ignore tiny changes
MAX_STEP_DEG = 6      # max degrees per update step
SEND_HZ = 20          # serial command rate (Hz)

# Macro
LAST_MACRO_PATH = "last_macro.csv"
MACRO_DURATION_S = 3.0
PLAY_HZ = 30

# RPS game
SHAKE_WINDOW = 15
SHAKE_THRESHOLD = 0.10
SHAKE_COOLDOWN_S = 1.2