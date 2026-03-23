import yaml
from pathlib import Path
from config.config import Config

def load_yaml(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_classes():
    data = load_yaml(Config.YAML_PATH)
    return data.get('names', [])

def print_project_info():
    print("="*50)
    print("YOLOv8 目标检测项目")
    print("="*50)
    Config.print_device_info()
    print(f"使用自定义模型: {Config.USE_CUSTOM_MODEL}")
    print(f"训练轮数: {Config.EPOCHS}")
    print(f"批次大小: {Config.BATCH_SIZE}")
    print(f"输入尺寸: {Config.IMG_SIZE}")
    print("="*50)