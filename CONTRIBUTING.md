# Contributing to GRIP-5

Thanks for your interest in GRIP-5! Contributions of all kinds are welcome —
bug reports, documentation fixes, calibration tips, new features, and hardware
notes.

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a bug** — open an issue using the bug report template.
- **Suggest a feature** — open an issue using the feature request template.
- **Improve docs** — fix or expand the README, the `docs/` guides, or wiring notes.
- **Submit code** — open a pull request (see below).

## Development setup

1. Fork and clone the repo:
   ```bash
   git clone https://github.com/<your-username>/GRIP-5.git
   cd GRIP-5
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Flash `mcu/mcu.ino` to an Arduino Uno R4 WiFi via the Arduino IDE.

You can develop and test most of the Python pipeline with just a webcam — the
preview window shows the landmark overlay and `DEBUG = True` in `config.py`
prints the per-finger values, so you don't always need the hardware attached.

## Project layout

| File / dir         | Responsibility |
| ------------------ | -------------- |
| `config.py`        | Tunables: thresholds, EMA, IP/port, model path |
| `gesture_logic.py` | Pure geometry: joint angles → openness values |
| `transport.py`     | Serial and UDP transports behind one interface |
| `drawing.py`       | Landmark overlay |
| `rps.py`           | Rock-Paper-Scissors game mode |
| `main.py`          | Camera loop + MediaPipe callback wiring |
| `mcu/mcu.ino`      | Arduino firmware (parsing + servo easing) |

Keep modules focused: geometry stays pure (no I/O), transports stay behind the
common `send()` / `close()` interface, and hardware-specific constants live in
`config.py` or the firmware rather than scattered through the code.

## Pull request process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your change. Test it:
   - Python changes: run `python main.py --mode serial` (or `wireless`) and
     confirm tracking still works; if you touched the game, test `--game`.
   - Firmware changes: confirm it compiles and the hand still responds.
3. Update docs if behavior changed (README, `docs/`, or this file).
4. Commit with a clear message describing **what** changed and **why**.
5. Push and open a pull request against `main`, filling in the PR template.

## Code style

- Python: follow PEP 8 where reasonable; keep functions small and named clearly.
- Prefer descriptive names over comments, but comment the non-obvious geometry
  and timing decisions (there are several).
- Don't commit secrets, large binaries, or your local `ARDUINO_IP`/port if it's
  specific to your network — keep those changes out of shared commits.

## Questions

Open a [Discussion](https://github.com/SUNSET-Sejong-University/GRIP-5/discussions)
or an issue. We're happy to help.
