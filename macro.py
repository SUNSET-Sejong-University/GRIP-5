# macro.py
import time
import csv
from dataclasses import dataclass

@dataclass
class MacroFrame:
    t: float
    angles: list

class MacroRecorder:
    def __init__(self):
        self.frames = []
        self.recording = False
        self.t0 = 0.0
        self.duration = 3.0

    def start(self, duration_s=3.0):
        self.frames = []
        self.recording = True
        self.duration = float(duration_s)
        self.t0 = time.time()

    def update(self, angles):
        if not self.recording:
            return
        t = time.time() - self.t0
        self.frames.append(MacroFrame(t=t, angles=list(map(int, angles))))
        if t >= self.duration:
            self.recording = False

    def time_left(self):
        if not self.recording:
            return 0.0
        return max(0.0, self.duration - (time.time() - self.t0))

    def save_csv(self, path):
        if not self.frames:
            raise RuntimeError("No macro frames to save.")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t", "idx", "mid", "ring", "little", "thumb"])
            for fr in self.frames:
                w.writerow([f"{fr.t:.4f}"] + fr.angles)

class MacroPlayer:
    def __init__(self, play_hz=30):
        self.frames = []
        self.playing = False
        self.loop = False
        self.t0 = 0.0
        self.i = 0
        self.play_hz = play_hz
        self._last_send_t = 0.0

    def load_csv(self, path):
        self.frames = []
        with open(path, "r", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                t = float(row["t"])
                angles = [
                    int(row["idx"]), int(row["mid"]), int(row["ring"]),
                    int(row["little"]), int(row["thumb"])
                ]
                self.frames.append(MacroFrame(t=t, angles=angles))
        if not self.frames:
            raise RuntimeError("Macro file is empty.")

    def start(self, loop=False):
        if not self.frames:
            raise RuntimeError("No macro loaded.")
        self.playing = True
        self.loop = bool(loop)
        self.t0 = time.time()
        self.i = 0
        self._last_send_t = 0.0

    def stop(self):
        self.playing = False

    def _interp(self, a, b, u):
        return [int(round(a[j] + u * (b[j] - a[j]))) for j in range(5)]

    def get_target_angles(self):
        if not self.playing:
            return None

        now = time.time()
        if now - self._last_send_t < 1.0 / self.play_hz:
            return None
        self._last_send_t = now

        t = now - self.t0

        while self.i + 1 < len(self.frames) and self.frames[self.i + 1].t < t:
            self.i += 1

        if self.i >= len(self.frames) - 1:
            if self.loop:
                self.start(loop=True)
                return self.frames[0].angles
            self.playing = False
            return None

        f0 = self.frames[self.i]
        f1 = self.frames[self.i + 1]
        dt = f1.t - f0.t
        if dt <= 1e-6:
            return f1.angles

        u = (t - f0.t) / dt
        u = max(0.0, min(1.0, u))
        return self._interp(f0.angles, f1.angles, u)