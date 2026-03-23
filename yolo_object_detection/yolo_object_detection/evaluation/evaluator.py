from config.config import Config
from models.model import YOLOv8Model


class Evaluator:
    def __init__(self):
        self.model = YOLOv8Model(mode='eval').get_model()

    def evaluate(self, split='val'):
        print(f"开始在 {split} 集上评估...")

        metrics = self.model.val(
            data=str(Config.YAML_PATH),
            split=split,
            imgsz=Config.IMG_SIZE,
            batch=Config.BATCH_SIZE,
            device=Config.DEVICE,
            project=str(Config.EVAL_OUTPUT_DIR),
            name=split,
            exist_ok=True
        )

        print(f"\n{split} 集评估结果:")
        print(f"mAP50: {metrics.box.map50:.4f}")
        print(f"mAP50-95: {metrics.box.map:.4f}")

        return metrics