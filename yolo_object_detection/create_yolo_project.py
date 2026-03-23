import os


def create_yolo_project_structure(base_path="yolo_object_detection"):
    """
    创建YOLO目标检测项目的文件夹和文件结构
    """
    # 定义项目结构
    structure = {
        "config": ["config.py"],
        "data": ["dataset.py"],
        "models": ["model.py"],
        "training": ["trainer.py"],
        "evaluation": ["evaluator.py"],
        "inference": ["predictor.py"],
        "utils": ["helpers.py"],
        "visualization": ["visualizer.py"],
        "configs": ["yolov8_custom.yaml"],
    }

    # 根目录下的文件
    root_files = ["main.py", "requirements.txt"]

    print(f"开始创建YOLO项目结构在: {os.path.abspath(base_path)}")
    print("=" * 50)

    # 创建基目录
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        print(f"✓ 创建目录: {base_path}/")
    else:
        print(f"⚠ 目录已存在: {base_path}/")

    # 创建所有子目录和文件
    for directory, files in structure.items():
        dir_path = os.path.join(base_path, directory)

        # 创建目录
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✓ 创建目录: {base_path}/{directory}/")
        else:
            print(f"⚠ 目录已存在: {base_path}/{directory}/")

        # 创建目录中的文件
        for file in files:
            file_path = os.path.join(dir_path, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 根据文件类型添加基本内容
                    if file.endswith('.py'):
                        f.write(f'# {directory}/{file}\n')
                        f.write(f'# YOLO Object Detection - {directory.capitalize()} Module\n')
                        f.write('# ' + '=' * 50 + '\n')
                        f.write(
                            f'"""\n{file.split(".")[0].capitalize()} module for YOLO object detection project.\n"""\n\n')
                        f.write('import os\nimport sys\n\n')
                        if file == 'config.py':
                            f.write('class Config:\n')
                            f.write('    """Configuration management class."""\n')
                            f.write('    def __init__(self):\n')
                            f.write('        self.model_name = "yolov8_custom"\n')
                            f.write('        self.input_size = (640, 640)\n')
                            f.write('        self.num_classes = 80\n')
                            f.write('        self.batch_size = 16\n')
                            f.write('        self.epochs = 100\n')
                            f.write('        self.learning_rate = 0.001\n')
                    elif file.endswith('.yaml'):
                        f.write('# YOLOv8 Custom Configuration\n')
                        f.write('# ' + '=' * 40 + '\n\n')
                        f.write('# Model parameters\n')
                        f.write('nc: 80  # number of classes\n')
                        f.write('depth_multiple: 0.33  # model depth multiple\n')
                        f.write('width_multiple: 0.50  # layer channel multiple\n\n')
                        f.write('# Training parameters\n')
                        f.write('lr0: 0.01  # initial learning rate\n')
                        f.write('lrf: 0.01  # final learning rate\n')
                        f.write('momentum: 0.937  # SGD momentum\n')
                        f.write('weight_decay: 0.0005  # optimizer weight decay\n')
                print(f"  ✓ 创建文件: {base_path}/{directory}/{file}")
            else:
                print(f"  ⚠ 文件已存在: {base_path}/{directory}/{file}")

    # 创建根目录下的文件
    for file in root_files:
        file_path = os.path.join(base_path, file)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                if file == 'main.py':
                    f.write('# main.py\n')
                    f.write('# YOLO Object Detection - Main Entry Point\n')
                    f.write('# ' + '=' * 50 + '\n')
                    f.write('"""\nMain script for YOLO object detection project.\n"""\n\n')
                    f.write('import os\nimport sys\n\n')
                    f.write('# Add project root to path\n')
                    f.write('sys.path.append(os.path.dirname(os.path.abspath(__file__)))\n\n')
                    f.write('from config.config import Config\n')
                    f.write('from training.trainer import Trainer\n')
                    f.write('from inference.predictor import Predictor\n\n')
                    f.write('def main():\n')
                    f.write('    """Main function."""\n')
                    f.write('    print("YOLO Object Detection Project")\n')
                    f.write('    print("=" * 50)\n\n')
                    f.write('    # Initialize configuration\n')
                    f.write('    config = Config()\n')
                    f.write('    print(f"Model: {config.model_name}")\n')
                    f.write('    print(f"Input size: {config.input_size}")\n\n')
                    f.write('    # TODO: Add training and inference logic\n')
                    f.write('    # trainer = Trainer(config)\n')
                    f.write('    # trainer.train()\n\n')
                    f.write('    # predictor = Predictor(config)\n')
                    f.write('    # results = predictor.predict("path/to/image.jpg")\n\n')
                    f.write('if __name__ == "__main__":\n')
                    f.write('    main()\n')
                elif file == 'requirements.txt':
                    f.write('# YOLO Object Detection Project Requirements\n')
                    f.write('# ' + '=' * 40 + '\n\n')
                    f.write('# Core dependencies\n')
                    f.write('ultralytics==8.0.0\n')
                    f.write('torch>=1.7.0\n')
                    f.write('torchvision>=0.8.0\n')
                    f.write('opencv-python>=4.5.0\n')
                    f.write('numpy>=1.19.0\n')
                    f.write('pandas>=1.2.0\n')
                    f.write('matplotlib>=3.3.0\n')
                    f.write('pillow>=8.0.0\n')
                    f.write('scikit-learn>=0.24.0\n\n')
                    f.write('# Additional utilities\n')
                    f.write('tqdm>=4.60.0\n')
                    f.write('seaborn>=0.11.0\n')
                    f.write('pyyaml>=5.4.0\n')
                    f.write('easydict>=1.9\n')
            print(f"✓ 创建文件: {base_path}/{file}")
        else:
            print(f"⚠ 文件已存在: {base_path}/{file}")

    print("=" * 50)
    print(f"项目结构创建完成!")
    print(f"项目位置: {os.path.abspath(base_path)}")

    # 显示创建的结构树
    print("\n项目结构:")
    print_project_tree(base_path)


def print_project_tree(base_path, prefix=""):
    """打印项目结构树"""
    items = os.listdir(base_path)
    items.sort()

    for i, item in enumerate(items):
        path = os.path.join(base_path, item)
        is_last = (i == len(items) - 1)

        if os.path.isdir(path):
            print(f"{prefix}{'└── ' if is_last else '├── '}{item}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            # 只打印下一级目录内容
            sub_items = os.listdir(path)
            sub_items.sort()
            for j, sub_item in enumerate(sub_items):
                sub_is_last = (j == len(sub_items) - 1)
                print(f"{new_prefix}{'└── ' if sub_is_last else '├── '}{sub_item}")
        else:
            print(f"{prefix}{'└── ' if is_last else '├── '}{item}")


if __name__ == "__main__":
    # 获取当前目录
    current_dir = os.getcwd()

    # 询问用户项目创建位置
    print("YOLO项目结构生成器")
    print("=" * 50)
    print(f"当前目录: {current_dir}")

    choice = input("是否在当前目录创建项目? (y/n): ").lower().strip()

    if choice == 'y':
        project_name = "yolo_object_detection"
        create_yolo_project_structure(project_name)
    else:
        project_path = input("请输入项目路径 (相对或绝对路径): ").strip()
        if not project_path:
            project_path = "yolo_object_detection"
        create_yolo_project_structure(project_path)

    print("\n下一步:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 运行项目: python main.py")
    print("3. 根据您的需求修改各个模块的代码")