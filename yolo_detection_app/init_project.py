import os

# 定义项目根目录（脚本所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 需要创建的目录结构（相对路径）
DIRS = [
    "config",
    "model",
    "ui",
    "utils",
    "weights",
    "logs",
]

# 需要创建的文件（相对路径及初始内容）
FILES = {
    "config/settings.py": "# Configuration settings\n",
    "model/detector.py": "# YOLO detection model wrapper\n",
    "ui/main_window.py": "# Main UI window\n",
    "utils/log_handler.py": "# Logging utilities\n",
    "weights/best.pt": "",  # 空文件作为占位
    # main.py 放在根目录
    "main.py": "#!/usr/bin/env python\n# Entry point of the application\n",
}

def create_structure():
    """创建项目目录和文件"""
    # 创建所有目录
    for dir_name in DIRS:
        dir_path = os.path.join(BASE_DIR, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

    # 创建所有文件
    for file_rel_path, content in FILES.items():
        file_path = os.path.join(BASE_DIR, file_rel_path)
        # 确保父目录存在（weights 目录已创建，但以防万一）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {file_path}")
        else:
            print(f"File already exists, skipping: {file_path}")

if __name__ == "__main__":
    create_structure()
    print("\nProject structure initialized successfully.")