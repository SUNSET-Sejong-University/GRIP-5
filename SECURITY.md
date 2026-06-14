# Security Policy

GRIP-5 is a research / educational hardware project. It controls servo motors
from a host PC over USB serial or WiFi (UDP). It is **not** hardened for use on
untrusted networks, and the wireless protocol is unauthenticated by design.

## Supported versions

| Version       | Supported |
| ------------- | --------- |
| latest `main` | ✅        |
| older commits | ❌        |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

- Preferred: open a private report via GitHub
  (**Security → Report a vulnerability** on this repository), or
- Email the maintainers at: `prithwisd@sju.ac.kr`  
Please include a description, steps to reproduce, and the potential impact.
We aim to acknowledge reports within a few days.

## Scope notes

- The UDP transport accepts any well-formed packet on its port. Run it only on a
  trusted LAN or the Arduino's own access point, never on a public network.
- The firmware exposes no remote-code paths; the worst case from a malformed
  packet is unintended servo motion.
