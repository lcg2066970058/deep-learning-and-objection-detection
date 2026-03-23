from config.config import Config
from models.model import YOLOv8Model


class Trainer:
    def __init__(self):
        Config.create_dirs()
        Config.print_device_info()
        self.model_wrapper = YOLOv8Model(mode='train')
        self.model = self.model_wrapper.get_model()

    def train(self):
        print("开始训练...")

        results = self.model.train(
            data=str(Config.YAML_PATH),
            epochs=Config.EPOCHS,
            batch=Config.BATCH_SIZE,
            imgsz=Config.IMG_SIZE,
            device=Config.DEVICE,
            workers=Config.WORKERS,
            project=str(Config.TRAIN_OUTPUT_DIR.parent),
            name=Config.TRAIN_OUTPUT_DIR.name,
            exist_ok=True,
            patience=50,
            save=True,
            plots=True
        )

        print("训练完成")
        return results