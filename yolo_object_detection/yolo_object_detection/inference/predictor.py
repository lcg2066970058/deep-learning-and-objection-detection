from pathlib import Path
from ultralytics import YOLO
from config.config import Config


class Predictor:
    def __init__(self):
        weights_path = Config.TRAIN_OUTPUT_DIR / "weights" / "best.pt"
        if not weights_path.exists():
            raise FileNotFoundError(f"未找到模型权重: {weights_path}，请先训练模型")

        self.model = YOLO(str(weights_path))
        Config.create_dirs()

    def predict_image(self, image_path, save=True):
        print(f"预测图片: {image_path}")

        results = self.model(
            str(image_path),
            conf=Config.CONF_THRESHOLD,
            iou=Config.IOU_THRESHOLD,
            device=Config.DEVICE,
            save=save,
            project=str(Config.PRED_OUTPUT_DIR),
            name="single_pred",
            exist_ok=True
        )

        return results

    def predict_folder(self, folder_path, save=True):
        print(f"批量预测文件夹: {folder_path}")

        results = self.model(
            str(folder_path),
            conf=Config.CONF_THRESHOLD,
            iou=Config.IOU_THRESHOLD,
            device=Config.DEVICE,
            save=save,
            project=str(Config.PRED_OUTPUT_DIR),
            name="batch_pred",
            exist_ok=True
        )

        return results