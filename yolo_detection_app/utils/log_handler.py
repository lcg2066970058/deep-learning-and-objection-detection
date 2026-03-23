# Logging utilities
from datetime import datetime
from pathlib import Path
from config.settings import LOG_DIR


class LogHandler:
    @staticmethod
    def calculate_stats(feedback_records: list):
        """
        计算统计数据
        :param feedback_records: 反馈记录列表
        :return: 统计结果字典
        """
        total = len(feedback_records)
        if total == 0:
            return None

        correct = 0
        incorrect = 0
        for record in feedback_records:
            if record["feedback"] == "correct":
                correct += 1
            elif record["feedback"] == "incorrect":
                incorrect += 1

        accuracy = (correct / total) * 100
        error_rate = (incorrect / total) * 100

        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": accuracy,
            "error_rate": error_rate
        }

    @staticmethod
    def save_log(stats: dict):
        """
        保存日志到文件
        :param stats: 统计结果字典
        """
        # 自动创建日志文件夹
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        # 按天生成日志文件
        log_file = LOG_DIR / f"检测日志_{datetime.now().strftime('%Y-%m-%d')}.txt"

        # 日志内容
        log_content = (
            f"\n==================== 检测记录 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ====================\n"
            f"导入图片总数：{stats['total']} 张\n"
            f"检测正确：{stats['correct']} 张\n"
            f"检测错误：{stats['incorrect']} 张\n"
            f"检测正确率：{stats['accuracy']:.2f}%\n"
            f"检测错误率：{stats['error_rate']:.2f}%\n"
            f"==================================================================================================\n"
        )

        # 追加写入
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_content)

    @staticmethod
    def print_stats_to_console(stats: dict):
        """打印统计结果到命令窗口"""
        print("\n" + "=" * 50)
        print("检测任务完成，统计结果：")
        print(f"导入图片总数：{stats['total']} 张")
        print(f"检测正确：{stats['correct']} 张")
        print(f"检测错误：{stats['incorrect']} 张")
        print(f"检测正确率：{stats['accuracy']:.2f}%")
        print(f"检测错误率：{stats['error_rate']:.2f}%")
        print("=" * 50 + "\n")