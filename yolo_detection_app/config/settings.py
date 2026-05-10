from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 模型配置
MODEL_PATH = BASE_DIR / "weights/best.pt"
DETECT_CONF_THRESHOLD = 0.5  # 检测置信度阈值，改这里就行

# 文件夹配置
LOG_DIR = BASE_DIR / "logs"
WEIGHTS_DIR = BASE_DIR / "weights"

# 界面固定尺寸
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 780
IMG_DISPLAY_WIDTH = 820
IMG_DISPLAY_HEIGHT = 580

# 支持的图片格式
SUPPORT_IMG_SUFFIX = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]

# 摄像头配置
VIDEO_FPS = 30

# 导出目录
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# 版本号
APP_VERSION = "2.0.0"
APP_NAME = "YOLOv8 目标检测系统"

# 最近打开路径配置
LAST_OPEN_PATH = BASE_DIR / "config/last_path.json"
