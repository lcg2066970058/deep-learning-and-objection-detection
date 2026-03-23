import argparse
import sys
from pathlib import Path

from config.config import Config
from data.dataset import DataLoader
from training.trainer import Trainer
from evaluation.evaluator import Evaluator
from inference.predictor import Predictor
from utils.helpers import print_project_info, get_classes
from visualization.visualizer import Visualizer


def main():
    parser = argparse.ArgumentParser(description="YOLOv8 目标检测项目")
    parser.add_argument('--mode', type=str, required=True,
                        choices=['info', 'train', 'eval', 'predict', 'vis'],
                        help='运行模式: info/train/eval/predict/vis')
    parser.add_argument('--input', type=str, help='预测模式时指定图片/文件夹路径')
    parser.add_argument('--split', type=str, default='val',
                        help='评估模式时指定数据集 split')

    args = parser.parse_args()

    if args.mode == 'info':
        print_project_info()
        try:
            data_loader = DataLoader()
            info = data_loader.get_data_info()
            print(f"\n数据集信息:")
            for split, count in info.items():
                print(f"  {split}: {count} 张")
            print(f"类别列表: {get_classes()}")
        except Exception as e:
            print(f"数据集未准备: {e}")

    elif args.mode == 'train':
        print_project_info()
        data_loader = DataLoader()
        trainer = Trainer()
        trainer.train()

    elif args.mode == 'eval':
        evaluator = Evaluator()
        evaluator.evaluate(split=args.split)

    elif args.mode == 'predict':
        if not args.input:
            print("预测模式需要指定 --input 参数")
            sys.exit(1)

        predictor = Predictor()
        input_path = Path(args.input)

        if input_path.is_file():
            predictor.predict_image(input_path)
        elif input_path.is_dir():
            predictor.predict_folder(input_path)
        else:
            print(f"输入路径不存在: {input_path}")

    elif args.mode == 'vis':
        Visualizer.plot_training_curves()


if __name__ == "__main__":
    main()