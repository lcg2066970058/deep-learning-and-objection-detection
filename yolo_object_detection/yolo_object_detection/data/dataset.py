from pathlib import Path
from config.config import Config


class DataLoader:
    def __init__(self):
        self.yaml_path = Config.YAML_PATH
        self._validate_dataset()

    def _validate_dataset(self):
        if not self.yaml_path.exists():
            raise FileNotFoundError(
                f"数据集配置文件不存在: {self.yaml_path}\n"
                f"请将 yolo_dataset 文件夹复制到: {Config.DATA_DIR.parent}"
            )

        for split in ['train', 'val', 'test']:
            img_dir = Config.DATA_DIR / "images" / split
            if not img_dir.exists():
                raise FileNotFoundError(f"图片文件夹不存在: {img_dir}")

        print("数据集验证通过")

    def get_data_info(self):
        info = {}
        for split in ['train', 'val', 'test']:
            img_dir = Config.DATA_DIR / "images" / split
            info[split] = len(list(img_dir.glob("*.jpg")))
        return info