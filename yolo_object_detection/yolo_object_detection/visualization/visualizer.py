import matplotlib.pyplot as plt
from pathlib import Path
from config.config import Config


class Visualizer:
    @staticmethod
    def plot_training_curves():
        results_csv = Config.TRAIN_OUTPUT_DIR / "results.csv"
        if not results_csv.exists():
            print("未找到训练结果文件，请先运行训练")
            return

        import pandas as pd
        df = pd.read_csv(results_csv)

        plt.figure(figsize=(10, 6))
        plt.plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP50')
        plt.plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP50-95')
        plt.xlabel('Epoch')
        plt.ylabel('mAP')
        plt.title('Training mAP Curves')
        plt.legend()
        plt.grid(True)

        save_path = Config.EVAL_OUTPUT_DIR / "training_curves.png"
        plt.savefig(save_path)
        print(f"训练曲线已保存至: {save_path}")
        plt.show()