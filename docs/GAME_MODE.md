# Rock-Paper-Scissors Game Mode

GRIP-5 includes a game mode in which the robotic hand plays Rock-Paper-Scissors
against you. Rounds play **automatically in a loop**: the hand counts down, you
throw, the hand reveals its own (randomly chosen) move, the result is shown, and
then it resets and the next round begins.

---

## Running it

```bash
python main.py --mode wireless --game     # wireless + game
python main.py --mode serial   --game     # serial + game
```

Omit `--game` for normal gesture mirroring. Press **`q`** in the preview window
to quit. The `--game` flag is read once at launch, so game mode is on for the
whole session.

---

## The three throws

The hand can only form three poses, expressed in the standard 5-digit protocol
(`index → middle → ring → pinky → thumb`, where `0` = closed and `9` = open):

| Throw    | Command string | Shape                   |
| -------- | -------------- | ----------------------- |
| Rock     | `00000`        | fist                    |
| Paper    | `99999`        | open hand               |
| Scissors | `99000`        | index + middle extended |

If your gesture isn't one of the three recognised shapes at the reveal moment,
the round is scored as **no valid throw**.

---

## How your gesture is classified

Your hand streams continuous `0–9` levels with jitter, so the live signal never
equals these strings *exactly*. Instead each finger is thresholded to
open/closed using `OPEN_THRESHOLD` (default `5`): a level `>= OPEN_THRESHOLD`
counts as open. The shape is then matched:

- all five fingers closed → **Rock**
- all five fingers open → **Paper**
- index + middle open, ring + pinky closed → **Scissors**
- anything else → **no throw**

The **thumb is intentionally ignored** for scissors, because people instinctively
stick the thumb out when making a "scissors" gesture. Requiring it closed would
reject most real throws.

If your fists aren't registering as Rock, raise `OPEN_THRESHOLD`; if open hands
aren't registering as Paper, lower it.

---

## Round flow (state machine)

```
idle ──> countdown ──> reveal ──> result ──> idle pause ──> (repeat)
```

| State      | Duration           | Hand shows        | What happens |
| ---------- | ------------------ | ----------------- | ------------ |
| countdown  | 3 s                | fist (`00000`)    | "Rock… Paper… Scissors!" 3-2-1 overlay |
| reveal     | instant            | the robot's throw | your gesture is classified and scored |
| result     | 3 s                | the robot's throw | shows Robot vs You and the outcome |
| idle pause | `IDLE_PAUSE` (2 s) | fist (`00000`)    | breather before the next round |

The next round starts on its own — there are no keys to press.

---

## Fair play

The robot commits its throw with `random.choice(THROWS)` **at the start of the
round, before it ever reads your hand.** This guarantees it can't peek at your
gesture and pick a winning counter — throws are uniformly random and independent
each round.

---

## On-screen overlay

- **Countdown:** a large 3-2-1 counter plus the "Rock… Paper… Scissors!" prompt.
- **Result:** the robot's throw, your throw (or `--` for no valid throw), and the
  outcome (win / lose / tie).

---

## Tuning

All in `rps.py`:

| Setting          | Effect                                          |
| ---------------- | ----------------------------------------------- |
| `OPEN_THRESHOLD` | open/closed cutoff on the 0–9 scale (default 5) |
| countdown time   | how long the 3-2-1 lasts before the reveal      |
| `IDLE_PAUSE`     | pause between rounds (default 2 s)              |

---

## Related files

- `rps.py` — game state machine, throw classification, scoring, overlay.
- `main.py` — wires the game into the MediaPipe callback (`game.update(steps)`).
