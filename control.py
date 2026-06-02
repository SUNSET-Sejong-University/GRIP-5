# control.py
import time
import math

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def angle_deg(a, b, c):
    """Angle ABC at point b using normalized landmark x,y."""
    abx, aby = a.x - b.x, a.y - b.y
    cbx, cby = c.x - b.x, c.y - b.y
    dot = abx * cbx + aby * cby
    nab = math.hypot(abx, aby)
    ncb = math.hypot(cbx, cby)
    if nab == 0 or ncb == 0:
        return 180.0
    cosv = clamp(dot / (nab * ncb), -1.0, 1.0)
    return math.degrees(math.acos(cosv))

def openness_from_angle(pip_angle, closed_angle, open_angle):
    return clamp((pip_angle - closed_angle) / (open_angle - closed_angle), 0.0, 1.0)

def openness_to_servo(open01, smin, smax):
    return int(round(smin + open01 * (smax - smin)))

def ema(prev, new, alpha):
    return prev + alpha * (new - prev)

def step_limit(prev, target, max_step):
    if target > prev + max_step:
        return prev + max_step
    if target < prev - max_step:
        return prev - max_step
    return target

class AngleController:
    """
    Handles smoothing, deadband, rate limit, and send scheduling.
    """
    def __init__(self, servo_mins, servo_maxs, alpha, deadband_deg, max_step_deg, send_hz):
        self.servo_mins = servo_mins
        self.servo_maxs = servo_maxs
        self.alpha = alpha
        self.deadband_deg = deadband_deg
        self.max_step_deg = max_step_deg
        self.send_hz = send_hz

        self.smooth = servo_mins[:]     # current smoothed angles
        self.last_sent = servo_mins[:]  # last sent angles
        self._last_send_t = 0.0

    def smooth_targets(self, targets):
        for i in range(5):
            sm = ema(self.smooth[i], targets[i], self.alpha)
            sm = step_limit(self.smooth[i], sm, self.max_step_deg)
            self.smooth[i] = int(round(sm))
        return self.smooth[:]

    def should_send(self, angles):
        now = time.time()
        if now - self._last_send_t < (1.0 / self.send_hz):
            return False
        if not any(abs(int(angles[i]) - int(self.last_sent[i])) >= self.deadband_deg for i in range(5)):
            return False
        self._last_send_t = now
        self.last_sent = list(map(int, angles))
        return True