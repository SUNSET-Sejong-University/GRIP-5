# game_rps.py
import time
import random
from collections import deque
from dataclasses import dataclass

@dataclass
class CountdownInfo:
    active: bool
    text: str
    seconds_left: float

class RPSGame:
    """
     "Reveal on shake" with on-screen countdown.
    Flow:
      - Detect shake => start countdown (e.g. 3..2..1..GO)
      - Pick robot move immediately, but only REVEAL after countdown ends
      - Cooldown prevents repeat triggers
    """
    def __init__(
        self,
        servo_mins,
        servo_maxs,
        shake_window=15,
        shake_threshold=0.10,
        cooldown_s=1.2,
        countdown_s=1.5,   # total countdown duration on screen
        reveal_delay_s=0.0 # extra delay after countdown (usually 0)
    ):
        self.servo_mins = servo_mins
        self.servo_maxs = servo_maxs

        self.wrist_hist = deque(maxlen=shake_window)
        self.shake_threshold = shake_threshold
        self.cooldown_s = cooldown_s
        self.last_trigger_time = 0.0

        # Countdown timing
        self.countdown_s = float(countdown_s)
        self.reveal_delay_s = float(reveal_delay_s)

        # State
        self.state = "IDLE"          # IDLE, COUNTDOWN, REVEALED
        self.t_start = 0.0           # when countdown started
        self.pending_choice = ""     # choice picked at trigger time
        self.last_choice = ""        # last revealed choice (for UI)

    def reset(self):
        self.wrist_hist.clear()
        self.state = "IDLE"
        self.pending_choice = ""
        self.last_choice = ""

    def pose_angles(self, name):
        IDX_MAX, MID_MAX, RNG_MAX, LIT_MAX, THM_MAX = self.servo_maxs
        IDX_MIN, MID_MIN, RNG_MIN, LIT_MIN, THM_MIN = self.servo_mins

        if name == "ROCK":
            return [IDX_MIN, MID_MIN, RNG_MIN, LIT_MIN, THM_MIN]
        if name == "PAPER":
            return [IDX_MAX, MID_MAX, RNG_MAX, LIT_MAX, THM_MAX]
        if name == "SCISSORS":
            return [IDX_MAX, MID_MAX, RNG_MIN, LIT_MIN, THM_MIN]
        return [IDX_MIN, MID_MIN, RNG_MIN, LIT_MIN, THM_MIN]

    def _shake_detected(self, landmarks):
        wrist = landmarks[0]
        self.wrist_hist.append((wrist.x, wrist.y))
        if len(self.wrist_hist) < self.wrist_hist.maxlen:
            return False

        dist = 0.0
        for i in range(1, len(self.wrist_hist)):
            x0, y0 = self.wrist_hist[i - 1]
            x1, y1 = self.wrist_hist[i]
            dist += ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        return dist > self.shake_threshold

    def get_countdown_info(self) -> CountdownInfo:
        if self.state != "COUNTDOWN":
            return CountdownInfo(active=False, text="", seconds_left=0.0)

        now = time.time()
        elapsed = now - self.t_start
        left = max(0.0, self.countdown_s - elapsed)

        # Build 3..2..1..GO style text
        # Example mapping for countdown_s ~1.5:
        # left > 1.0 => "3", left > 0.5 => "2", left > 0.0 => "1"
        # and when left == 0 => "GO"
        # You can tune these thresholds if you change countdown_s.
        if left > 1.0:
            txt = "3"
        elif left > 0.5:
            txt = "2"
        elif left > 0.0:
            txt = "1"
        else:
            txt = "GO"

        return CountdownInfo(active=True, text=txt, seconds_left=left)

    def update(self, landmarks):
        """
        Call this every callback while in GAME mode.
        Returns:
          - None if no pose should be sent now
          - [5 angles] when it's time to reveal robot's move
        """
        now = time.time()

        # 1) If we are counting down, reveal when countdown ends (+ optional reveal delay)
        if self.state == "COUNTDOWN":
            if (now - self.t_start) >= (self.countdown_s + self.reveal_delay_s):
                self.state = "REVEALED"
                self.last_choice = self.pending_choice
                return self.pose_angles(self.pending_choice)
            return None

        # 2) If idle, check cooldown and shake to trigger a new round
        if self.state == "IDLE":
            if (now - self.last_trigger_time) <= self.cooldown_s:
                return None

            if self._shake_detected(landmarks):
                self.last_trigger_time = now
                self.pending_choice = random.choice(["ROCK", "PAPER", "SCISSORS"])
                self.t_start = now
                self.state = "COUNTDOWN"
                return None

        # 3) After revealing, wait for next shake (after cooldown) to start next round
        if self.state == "REVEALED":
            # allow a new round after cooldown; we reuse IDLE so it can trigger again
            if (now - self.last_trigger_time) > self.cooldown_s:
                self.state = "IDLE"
            return None

        return None