# vision.py
import mediapipe as mp
from mediapipe.tasks.python import vision

class HandVision:
    def __init__(self, model_path, callback):
        self.model_path = model_path
        self.callback = callback

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        self._HandLandmarker = HandLandmarker
        self._HandLandmarkerOptions = HandLandmarkerOptions
        self._BaseOptions = BaseOptions
        self._VisionRunningMode = VisionRunningMode

        self.landmarker = None

    def __enter__(self):
        options = self._HandLandmarkerOptions(
            base_options=self._BaseOptions(model_asset_path=self.model_path),
            running_mode=self._VisionRunningMode.LIVE_STREAM,
            result_callback=self.callback
        )
        self.landmarker = self._HandLandmarker.create_from_options(options)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.landmarker:
            self.landmarker.close()

    def detect_async(self, mp_image, timestamp_ms):
        self.landmarker.detect_async(mp_image, timestamp_ms)