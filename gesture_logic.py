import numpy as np

def _pt(landmarks, i):
    return np.array([landmarks[i].x, landmarks[i].y, landmarks[i].z])

def joint_angle(landmarks, a, b, c):
    """Angle (deg) at vertex b for the a-b-c chain, ~180 = straight, small = curled"""
    v1 = _pt(landmarks, a) - _pt(landmarks, b)
    v2 = _pt(landmarks, c) - _pt(landmarks, b)
    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def norm_dist(landmarks, a, b, r1, r2):
    """Distance a-b normalized by reference length r1-r2 (scale-invariant)"""
    d = np.linalg.norm(_pt(landmarks,a) - _pt(landmarks, b))
    ref = np.linalg.norm(_pt(landmarks, r1) - _pt(landmarks, r2)) + 1e-6
    return d / ref 

def remap01(value, lo, hi):
    """Map value from [lo, hi] to [0, 1], clamped"""
    return max(0.0, min(1.0, (value - lo) / (hi - lo + 1e-6)))