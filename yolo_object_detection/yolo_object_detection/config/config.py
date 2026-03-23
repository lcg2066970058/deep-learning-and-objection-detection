from pathlib import Path
import torch


class Config:
    BASE_DIR = Path(__file__).parent.parent

    # 数据集路径配置
    DATA_DIR = BASE_DIR / "datasets" / "yolo_dataset"
    YAML_PATH = DATA_DIR / "dataset.yaml"

    # 模型配置
    USE_CUSTOM_MODEL = False
    CUSTOM_MODEL_CFG = BASE_DIR / "configs" / "yolov8_custom.yaml"
    MODEL_SIZE = "n"
    PRETRAINED_WEIGHTS = f"yolov8{MODEL_SIZE}.pt"

    # 训练配置（默认启用 CUDA）
    EPOCHS = 100
    BATCH_SIZE = 16
    IMG_SIZE = 640
    # 自动检测 CUDA 是否可用，不可用则回退到 CPU
    DEVICE = "0" if torch.cuda.is_available() else "cpu"
    WORKERS = 4

    # 输出路径
    OUTPUT_DIR = BASE_DIR / "outputs"
    TRAIN_OUTPUT_DIR = OUTPUT_DIR / "train"
    EVAL_OUTPUT_DIR = OUTPUT_DIR / "eval"
    PRED_OUTPUT_DIR = OUTPUT_DIR / "pred"

    # 推理阈值
    CONF_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45

    @classmethod
    def create_dirs(cls):
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TRAIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.EVAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.PRED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def print_device_info(cls):
        print(f"PyTorch 版本: {torch.__version__}")
        if torch.cuda.is_available():
            print(f"CUDA 可用: True")
            print(f"GPU 数量: {torch.cuda.device_count()}")
            print(f"当前 GPU: {torch.cuda.get_device_name(0)}")
        else:
            print(f"CUDA 可用: False，将使用 CPU")