import cv2

def draw_landmarks(image, hand_landmarks_list, connections):
    """Draw landmark points and finger connections onto the image frame"""
    h, w, _ = image.shape
    for hand_landmarks in hand_landmarks_list:
        # points
        for landmark in hand_landmarks:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
        # connections
        for start_idx, end_idx in connections:
            s, e = hand_landmarks[start_idx], hand_landmarks[end_idx]
            sp = (int(s.x * w), int(s.y * h))
            ep = (int(e.x * w), int(e.y * h))
            cv2.line(image, sp, ep, (255, 0, 0), 2)
            