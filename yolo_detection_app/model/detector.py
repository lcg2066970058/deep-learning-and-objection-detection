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

    def detect_image(self, img_path: str | Path):
        """
        检测单张图片
        :param img_path: 图片路径
        :return: ultralytics检测结果对象
        """
        if self.model is None:
            raise Exception("模型未加载成功！")

        results = self.model(str(img_path), conf=DETECT_CONF_THRESHOLD)
        return results[0]