from dataclasses import dataclass
import sys

import cv2
import numpy as np
import types

mp: types.ModuleType | None = None
try:
    import mediapipe as _mp

    mp = _mp
except ImportError:
    mp = None

_PERSON_CATEGORY = "person"


@dataclass(slots=True)
class VisionMetrics:
    motion_detected: bool
    motion_score: float
    brightness: float
    low_light: bool
    presence_detected: bool
    detections: list | None = None


class VisionAnalyzer:
    def __init__(
        self,
        motion_threshold: int = 25,
        min_motion_area: int = 500,
        low_light_threshold: float = 0.25,
        enable_detection: bool = True,
        detection_model_path: str = "model/efficientdet_lite0.tflite",
        detection_score_threshold: float = 0.5,
        process_resolution: tuple[int, int] = (640, 480),
        skip_frames: int = 5,
    ) -> None:
        self._motion_threshold = motion_threshold
        self._min_motion_area = min_motion_area
        self._low_light_threshold = low_light_threshold
        self._process_resolution = process_resolution
        self._skip_frames = skip_frames

        self._frame_count = 0
        self._previous_gray: np.ndarray | None = None
        self._last_detections = None
        self._last_presence = False

        self._detector = None
        if enable_detection:
            self._detector = self._create_object_detector(
                detection_model_path, detection_score_threshold
            )

    def _create_object_detector(self, model_path: str, score_threshold: float):
        if mp is None:
            print(
                "Aviso: MediaPipe não encontrado; detecção de presença desativada.",
                file=sys.stderr,
            )
            return None

        try:
            BaseOptions = mp.tasks.BaseOptions
            ObjectDetector = mp.tasks.vision.ObjectDetector
            ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
            VisionRunningMode = mp.tasks.vision.RunningMode

            options = ObjectDetectorOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=VisionRunningMode.IMAGE,
                score_threshold=score_threshold,
                category_allowlist=[_PERSON_CATEGORY],
            )

            return ObjectDetector.create_from_options(options)

        except Exception as e:
            print(
                f"Aviso: Falha ao inicializar o ObjectDetector do MediaPipe. "
                f"Verifique se o arquivo '{model_path}' existe no diretório. "
                f"Detalhes: {e}",
                file=sys.stderr,
            )
            return None

    def process(self, frame: np.ndarray) -> VisionMetrics:
        small_frame = cv2.resize(frame, self._process_resolution)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        brightness = float(np.mean(gray) / 255.0)
        low_light = brightness < self._low_light_threshold

        motion_score = 0.0
        motion_detected = False
        if self._previous_gray is not None:
            frame_delta = cv2.absdiff(self._previous_gray, gray)
            thresh = cv2.threshold(
                frame_delta, self._motion_threshold, 255, cv2.THRESH_BINARY
            )[1]

            kernel = np.ones((3, 3), dtype=np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            area_sum = sum(
                cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 0
            )
            motion_detected = any(
                cv2.contourArea(c) >= self._min_motion_area for c in contours
            )
            frame_area = float(
                self._process_resolution[0] * self._process_resolution[1]
            )
            motion_score = min(1.0, area_sum / (frame_area * 0.20))

        self._previous_gray = gray
        self._frame_count += 1

        if self._detector is not None and mp is not None:
            if self._frame_count % self._skip_frames == 0:
                rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                detection_result = self._detector.detect(mp_image)

                self._last_detections = detection_result.detections
                self._last_presence = bool(self._last_detections)

        return VisionMetrics(
            motion_detected=motion_detected,
            motion_score=motion_score,
            brightness=brightness,
            low_light=low_light,
            presence_detected=self._last_presence,
            detections=self._last_detections,
        )

    def close(self) -> None:
        if self._detector is not None:
            self._detector.close()
