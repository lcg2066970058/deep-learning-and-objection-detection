# YOLO detection model wrapper
from ultralytics import YOLO
from pathlib import Path
from config.settings import MODEL_PATH, DETECT_CONF_THRESHOLD


class YoloDetector:
    def __init__(self):
        self.model = None
        self.class_names = None
        self._load_model()

    def _load_model(self):
        """加载模型，初始化类别名称"""
        if not Path(MODEL_PATH).exists():
            raise FileNotFoundError(f"模型文件不存在！请把best.pt放在路径：{MODEL_PATH}")

        self.model = YOLO(str(MODEL_PATH))
        self.class_names = self.model.names

    def detect_image(self, img_path: str | Path, conf: float = None):
        """
        检测单张图片
        :param img_path: 图片路径
        :param conf: 可选，覆盖默认置信度阈值
        :return: ultralytics检测结果对象
        """
        if self.model is None:
            raise Exception("模型未加载成功！")

        threshold = conf if conf is not None else DETECT_CONF_THRESHOLD
        results = self.model(str(img_path), conf=threshold)
        return results[0]

    def detect_frame(self, frame, conf: float = None):
        """
        检测视频帧（摄像头实时检测）
        :param frame: numpy array (BGR)
        :param conf: 可选，覆盖默认置信度阈值
        :return: ultralytics检测结果对象
        """
        if self.model is None:
            raise Exception("模型未加载成功！")

        threshold = conf if conf is not None else DETECT_CONF_THRESHOLD
        results = self.model(frame, conf=threshold, verbose=False)
        return results[0]