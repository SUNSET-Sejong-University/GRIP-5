import time
import random
import cv2

# the only three poses the hand throws (order: index, middle, ring, pinky, thumb)
ROCK     = "00000"                                              # fist
PAPER    = "99999"                                              # open hand
SCISSORS = "99000"                                              # index + middle out
THROWS   = [ROCK, PAPER, SCISSORS]
NAMES    = {ROCK: "Rock", PAPER: "Paper", SCISSORS: "Scissors"}
COUNTER  = {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}       # value beats key

OPEN_THRESHOLD = 5                                              # a finger is "open" if its 0-9 level is >= this value

def classify(steps):
    """Live 0-9 finger levels -> a throw, or None if it isn't a valid RPS pose."""
    if steps is None:
        return None
    openf = [s >= OPEN_THRESHOLD for s in steps]                # [idx, mid, ring, pinky, thumb]
    if openf == [False, False, False, False, False]:
        return ROCK
    if openf == [True, True, True, True, True]:
        return PAPER
    if openf[0] and openf[1] and not openf[2] and not openf[3]: # ignoring the thumb
        return SCISSORS
    return None


def beats(a, b):
    return COUNTER[b] == a


class RPSGame:
    def __init__(self, cheat=False):
        self.active = False
        self.cheat = cheat
        self.state = "idle"             # idle | countdown | result
        self.countdown_end = 0.0 
        self.result_until = 0.0
        self.robot_throw = None
        self.human_throw = None
        self.result_text = ""


    def toggle(self):
        self.active = not self.active
        self.state = "idle"
        return self.active
    

    def start_round(self):
        if not self.active or self.state == "countdown":
            return
        self.state = "countdown"
        self.countdown_end = time.time() + 3.0
        self.human_throw = None
        self.result_text = ""
        self.robot_throw = random.choice(THROWS)  # committing before the reveal -> fair game


    def update(self, steps):
        """Call every frame. Returns the string to send to the hand, or None to hold."""
        if not self.active:
            return None
        now = time.time()

        if self.state == "countdown":
            if now < self.countdown_end:
                return ROCK                     # hold a fist while counting down
            self.human_throw = classify(steps)  # reveal moment
            if self.cheat and self.human_throw is not None:
                self.robot_throw = COUNTER[self.human_throw]
            self._decide()
            self.state = "result"
            self.result_until = now + 3.0
            return self.robot_throw
        
        if self.state == "result":
            if now >= self.result_until:
                self.state = "idle"
                return ROCK
            return self.robot_throw             # hold the throw during the result
        
        return ROCK                             # idle but in game mode: ready fist
    

    def _decide(self):
        h, r = self.human_throw, self.robot_throw
        if h is None:
            self.result_text = "No valid throw - try again!"
        elif h == r:
            self.result_text = f"Tie ({NAMES[h]})"
        elif beats(r, h):
            self.result_text = f"Robot wins - {NAMES[r]} beats {NAMES[h]}"
        else:
            self.result_text = f"You win: {NAMES[h]} beats {NAMES[r]}"


    def draw_overlay(self, img):
        h, w = img.shape[:2]
        if self.state == "countdown":
            n = max(1, int(self.countdown_end - time.time()) + 1)
            cv2.putText(img, str(n), (w // 2 - 30, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 255), 5)
            cv2.putText(img, "Rock...Paper...Scissors!", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        elif self.state == "result":
            cv2.putText(img, f"Robot: {NAMES.get(self.robot_throw, '?')}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            cv2.putText(img, f"You: {NAMES.get(self.human_throw, '--')}", (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            cv2.putText(img, self.result_text, (20, 115),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        else:
            cv2.putText(img, "GAME MODE - press SPACE to throw", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)       