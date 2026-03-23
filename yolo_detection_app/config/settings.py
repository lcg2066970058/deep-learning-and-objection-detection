import sys
from pathlib import Path

# 自动判断环境：开发环境 / 打包后的exe环境
if getattr(sys, 'frozen', False):
    # 打包后：exe文件所在的目录
    BASE_DIR = Path(sys.executable).parent
else:
    # 开发时：项目根目录
    BASE_DIR = Path(__file__).parent.parent

# 模型配置
MODEL_PATH = BASE_DIR / "weights/best.pt"
DETECT_CONF_THRESHOLD = 0.5  # 检测置信度阈值

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