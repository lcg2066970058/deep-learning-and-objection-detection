from ultralytics import YOLO
from config.config import Config


class YOLOv8Model:
    def __init__(self, mode='train'):
        self.mode = mode
        self.model = None
        self._build_model()

    def _build_model(self):
        if self.mode == 'train':
            if Config.USE_CUSTOM_MODEL and Config.CUSTOM_MODEL_CFG.exists():
                self.model = YOLO(str(Config.CUSTOM_MODEL_CFG))
                print(f"已加载自定义模型结构: {Config.CUSTOM_MODEL_CFG.name}")
            else:
                self.model = YOLO(Config.PRETRAINED_WEIGHTS)
                print(f"已加载预训练模型: {Config.PRETRAINED_WEIGHTS}")
        else:
            weights_path = Config.TRAIN_OUTPUT_DIR / "weights" / "best.pt"
            if not weights_path.exists():
                raise FileNotFoundError(f"未找到模型权重: {weights_path}")
            self.model = YOLO(str(weights_path))
            print("已加载训练好的模型")

    def get_model(self):
        return self.model