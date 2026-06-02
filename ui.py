# ui.py
import cv2

def draw_center_text(img, text, y, scale=3.0, color=(0, 255, 255), thickness=6):
    h, w = img.shape[:2]
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    x = (w - tw) // 2
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

def draw_overlay(img, mode, last_sent, rec, player, rps_game):
    if img is None:
        return

    status = []
    if getattr(player, "playing", False):
        status.append("PLAY")
    if getattr(rec, "recording", False):
        status.append(f"REC {rec.time_left():.1f}s")
    if mode == "GAME":
        status.append("GAME (shake)")
        # show last revealed choice if any
        if getattr(rps_game, "last_choice", ""):
            status.append(f"LAST: {rps_game.last_choice}")
    if not status:
        status.append("LIVE")

    cv2.putText(img, " | ".join(status),
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255, 255, 0), 2)

    cv2.putText(img, "Keys: g=game  r=rec  p=play  s=stop  q=quit",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (0, 255, 255), 2)

    cv2.putText(img, f"Angles: {list(map(int, last_sent))}",
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (0, 255, 0), 2)

    # ---- Countdown overlay (GAME mode) ----
    if mode == "GAME":
        info = rps_game.get_countdown_info()
        if info.active:
            # Draw big countdown number in center
            h, w = img.shape[:2]
            draw_center_text(img, info.text, y=h//2, scale=4.0, color=(0, 255, 255), thickness=8)
            # Small helper text
            cv2.putText(img, "Reveal on GO!",
                        (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                        (0, 255, 255), 2)