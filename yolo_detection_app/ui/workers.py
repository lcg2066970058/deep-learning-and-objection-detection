import cv2
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from model.detector import YoloDetector


class DetectionWorker(QThread):
    """Background worker for batch image detection."""
    progress = pyqtSignal(int, int)  # current, total
    result_ready = pyqtSignal(int, object)  # index, results
    finished_all = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, detector: YoloDetector, img_list, conf=None):
        super().__init__()
        self.detector = detector
        self.img_list = img_list
        self.conf = conf
        self._running = True

    def run(self):
        total = len(self.img_list)
        for idx, img_path in enumerate(self.img_list):
            if not self._running:
                break
            try:
                results = self.detector.detect_image(img_path, conf=self.conf)
                self.result_ready.emit(idx, results)
            except Exception as e:
                self.error_occurred.emit(str(e))
            self.progress.emit(idx + 1, total)
        self.finished_all.emit()

    def stop(self):
        self._running = False
        self.wait(1000)


class CameraWorker(QThread):
    """Background worker for real-time camera detection."""
    frame_ready = pyqtSignal(np.ndarray)
    fps_updated = pyqtSignal(float)
    error_occurred = pyqtSignal(str)

    def __init__(self, detector: YoloDetector, conf=None, fps=30):
        super().__init__()
        self.detector = detector
        self.conf = conf
        self.target_fps = fps
        self._running = True
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.error_occurred.emit("无法打开摄像头，请检查设备连接")
            return

        # Set resolution and fps
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        frame_time = 1.0 / self.target_fps
        last_time = time.time()

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            try:
                results = self.detector.detect_frame(frame, conf=self.conf)
                annotated = results.plot()
                self.frame_ready.emit(annotated)
            except Exception as e:
                self.error_occurred.emit(str(e))

            # Simple FPS throttle
            elapsed = time.time() - last_time
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

            fps = 1.0 / (time.time() - last_time + 1e-6)
            last_time = time.time()
            self.fps_updated.emit(fps)

        self.cap.release()
        self.cap = None

    def stop(self):
        self._running = False
        self.wait(2000)
