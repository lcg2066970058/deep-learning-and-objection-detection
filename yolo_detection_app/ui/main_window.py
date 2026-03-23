# Main UI window
import sys
import cv2
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QLabel, QTextEdit, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from config.settings import *
from model.detector import YoloDetector
from utils.log_handler import LogHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 窗口基础配置
        self.setWindowTitle("YOLOv8 目标检测系统（带反馈统计）")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # 初始化核心组件
        try:
            self.detector = YoloDetector()
        except Exception as e:
            QMessageBox.critical(self, "模型加载失败", str(e))
            sys.exit(1)

        # 全局状态变量（仅在主窗口维护，不扩散到其他模块）
        self.img_list = []                # 待检测图片路径列表
        self.current_index = -1           # 当前图片索引
        self.current_results = None       # 当前图片检测结果
        self.feedback_records = []        # 用户反馈记录
        self.is_folder_mode = False       # 是否为文件夹模式

        # 初始化界面
        self._init_ui()

    def _init_ui(self):
        """初始化界面布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # 1. 顶部功能按钮区
        top_layout = QHBoxLayout()
        self.btn_select_single = QPushButton("选择单张图片")
        self.btn_select_single.setFixedSize(160, 40)
        self.btn_select_single.clicked.connect(self.select_single_image)

        self.btn_select_folder = QPushButton("选择图片文件夹")
        self.btn_select_folder.setFixedSize(160, 40)
        self.btn_select_folder.clicked.connect(self.select_image_folder)

        self.btn_exit = QPushButton("结束程序")
        self.btn_exit.setFixedSize(160, 40)
        self.btn_exit.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        self.btn_exit.clicked.connect(self.exit_app)

        top_layout.addWidget(self.btn_select_single)
        top_layout.addWidget(self.btn_select_folder)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_exit)
        main_layout.addLayout(top_layout)

        # 2. 中间内容区（图片+结果）
        content_layout = QHBoxLayout()
        # 左侧图片显示
        self.img_label = QLabel("请选择图片或文件夹")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f5f5f5;")
        self.img_label.setFixedSize(IMG_DISPLAY_WIDTH, IMG_DISPLAY_HEIGHT)
        content_layout.addWidget(self.img_label)

        # 右侧结果文本
        result_layout = QVBoxLayout()
        result_label = QLabel("检测结果详情")
        result_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFixedSize(420, IMG_DISPLAY_HEIGHT)
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_text)
        content_layout.addLayout(result_layout)

        main_layout.addLayout(content_layout)

        # 3. 反馈按钮区
        feedback_layout = QHBoxLayout()
        self.progress_label = QLabel("当前：0/0 张")
        self.progress_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.btn_correct = QPushButton("检测正确 ✔")
        self.btn_correct.setFixedSize(180, 45)
        self.btn_correct.setStyleSheet("background-color: #00C851; color: white; font-size: 14px; font-weight: bold;")
        self.btn_correct.clicked.connect(lambda: self.record_feedback("correct"))
        self.btn_correct.setEnabled(False)

        self.btn_incorrect = QPushButton("检测错误 ✖")
        self.btn_incorrect.setFixedSize(180, 45)
        self.btn_incorrect.setStyleSheet("background-color: #ff4444; color: white; font-size: 14px; font-weight: bold;")
        self.btn_incorrect.clicked.connect(lambda: self.record_feedback("incorrect"))
        self.btn_incorrect.setEnabled(False)

        feedback_layout.addWidget(self.progress_label)
        feedback_layout.addStretch()
        feedback_layout.addWidget(self.btn_correct)
        feedback_layout.addWidget(self.btn_incorrect)
        feedback_layout.addStretch()
        main_layout.addLayout(feedback_layout)

        # 4. 底部切换按钮区
        bottom_layout = QHBoxLayout()
        self.btn_prev = QPushButton("上一张")
        self.btn_prev.setFixedSize(160, 40)
        self.btn_prev.clicked.connect(self.show_prev_image)
        self.btn_prev.setEnabled(False)

        self.btn_next = QPushButton("下一张")
        self.btn_next.setFixedSize(160, 40)
        self.btn_next.clicked.connect(self.show_next_image)
        self.btn_next.setEnabled(False)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_prev)
        bottom_layout.addWidget(self.btn_next)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

    # ==================== 图片选择与加载 ====================
    def select_single_image(self):
        """选择单张图片"""
        self._reset_state()
        self.is_folder_mode = False

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", f"图片文件 ({' '.join(SUPPORT_IMG_SUFFIX)})"
        )
        if file_path:
            self.img_list = [Path(file_path)]
            self.current_index = 0
            self.detect_and_show()
            self._update_btn_state()
            self.progress_label.setText(f"当前：{self.current_index+1}/{len(self.img_list)} 张")

    def select_image_folder(self):
        """选择图片文件夹"""
        self._reset_state()
        self.is_folder_mode = True

        folder_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹", "")
        if folder_path:
            folder = Path(folder_path)
            # 加载所有支持的图片
            for suffix in SUPPORT_IMG_SUFFIX:
                self.img_list.extend(list(folder.glob(suffix)))
            self.img_list.sort()

            if len(self.img_list) == 0:
                QMessageBox.warning(self, "提示", "文件夹内未找到支持的图片文件！")
                return

            # 初始化反馈记录
            self.feedback_records = [{"img_path": img, "feedback": None} for img in self.img_list]
            # 显示第一张
            self.current_index = 0
            self.detect_and_show()
            self._update_btn_state()
            self.progress_label.setText(f"当前：{self.current_index+1}/{len(self.img_list)} 张")

    def _reset_state(self):
        """重置所有状态"""
        self.img_list = []
        self.current_index = -1
        self.current_results = None
        self.feedback_records = []
        self.is_folder_mode = False
        self.img_label.setText("请选择图片或文件夹")
        self.result_text.clear()
        self.progress_label.setText("当前：0/0 张")
        self.btn_correct.setEnabled(False)
        self.btn_incorrect.setEnabled(False)

    # ==================== 检测与显示 ====================
    def detect_and_show(self):
        """执行检测并更新界面显示"""
        if self.current_index < 0 or self.current_index >= len(self.img_list):
            return

        current_img_path = self.img_list[self.current_index]
        self.setWindowTitle(f"YOLOv8 目标检测系统 - 当前图片：{current_img_path.name}")

        # 调用检测器执行检测
        self.current_results = self.detector.detect_image(current_img_path)

        # 转换图片格式用于Qt显示
        annotated_img = self.current_results.plot()
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        height, width, channel = annotated_img.shape
        bytes_per_line = channel * width

        # 自适应缩放
        qimg = QImage(annotated_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.img_label.setPixmap(pixmap)

        # 更新结果文本
        self._update_result_text()
        # 重置反馈按钮状态
        self._reset_feedback_btn()

    def _update_result_text(self):
        """更新右侧检测结果文本"""
        if self.current_results is None:
            return

        img_name = self.img_list[self.current_index].name
        total_count = len(self.current_results.boxes)
        text = f"图片名称：{img_name}\n"
        text += f"检测到物体数量：{total_count}\n"
        text += "="*45 + "\n"

        if total_count == 0:
            text += "未检测到任何物体\n"
        else:
            for idx, box in enumerate(self.current_results.boxes):
                cls_id = int(box.cls[0])
                cls_name = self.detector.class_names[cls_id]
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                text += f"【物体 {idx+1}】\n"
                text += f"  类别：{cls_name}\n"
                text += f"  置信度：{conf:.2f}\n"
                text += f"  坐标：{bbox}\n"
                text += "-"*40 + "\n"

        # 显示反馈状态
        if self.is_folder_mode:
            current_feedback = self.feedback_records[self.current_index]["feedback"]
            text += "\n" + "="*45 + "\n"
            if current_feedback == "correct":
                text += "当前反馈：✅ 已标记【检测正确】"
            elif current_feedback == "incorrect":
                text += "当前反馈：❌ 已标记【检测错误】"
            else:
                text += "当前反馈：⏺️ 未标记，切换图片将默认【检测正确】"

        self.result_text.setText(text)

    # ==================== 反馈记录 ====================
    def _reset_feedback_btn(self):
        """重置反馈按钮状态"""
        if not self.is_folder_mode:
            self.btn_correct.setEnabled(False)
            self.btn_incorrect.setEnabled(False)
            return

        current_feedback = self.feedback_records[self.current_index]["feedback"]
        self.btn_correct.setEnabled(True)
        self.btn_incorrect.setEnabled(True)

        if current_feedback == "correct":
            self.btn_correct.setEnabled(False)
            self.btn_correct.setText("已标记正确")
            self.btn_incorrect.setText("检测错误 ✖")
        elif current_feedback == "incorrect":
            self.btn_incorrect.setEnabled(False)
            self.btn_incorrect.setText("已标记错误")
            self.btn_correct.setText("检测正确 ✔")
        else:
            self.btn_correct.setText("检测正确 ✔")
            self.btn_incorrect.setText("检测错误 ✖")

    def record_feedback(self, feedback_type):
        """记录用户反馈"""
        if not self.is_folder_mode or self.current_index < 0:
            return
        self.feedback_records[self.current_index]["feedback"] = feedback_type
        self._reset_feedback_btn()
        self._update_result_text()

    # ==================== 图片切换 ====================
    def show_prev_image(self):
        """切换上一张"""
        if self.current_index > 0:
            self.current_index -= 1
            self.detect_and_show()
            self._update_btn_state()
            self.progress_label.setText(f"当前：{self.current_index+1}/{len(self.img_list)} 张")

    def show_next_image(self):
        """切换下一张/结束统计"""
        # 未标记的默认正确
        if self.is_folder_mode and self.feedback_records[self.current_index]["feedback"] is None:
            self.record_feedback("correct")

        # 最后一张触发统计
        if self.current_index == len(self.img_list) - 1:
            self.show_final_stats()
            self.exit_app()
            return

        # 切换下一张
        if self.current_index < len(self.img_list) - 1:
            self.current_index += 1
            self.detect_and_show()
            self._update_btn_state()
            self.progress_label.setText(f"当前：{self.current_index+1}/{len(self.img_list)} 张")

    def _update_btn_state(self):
        """更新按钮可用状态"""
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(len(self.img_list) > 0)

        # 最后一张修改按钮文字
        if self.current_index == len(self.img_list) - 1 and len(self.img_list) > 0:
            self.btn_next.setText("结束并统计")
        else:
            self.btn_next.setText("下一张")

    # ==================== 统计与退出 ====================
    def show_final_stats(self):
        """显示最终统计结果"""
        stats = LogHandler.calculate_stats(self.feedback_records)
        if not stats:
            return

        # 输出到命令行
        LogHandler.print_stats_to_console(stats)
        # 弹窗显示给用户
        stats_text = (
            f"===== 检测统计结果 =====\n"
            f"导入图片总数：{stats['total']} 张\n"
            f"检测正确：{stats['correct']} 张\n"
            f"检测错误：{stats['incorrect']} 张\n"
            f"检测正确率：{stats['accuracy']:.2f}%\n"
            f"检测错误率：{stats['error_rate']:.2f}%\n"
            f"========================"
        )
        QMessageBox.information(self, "检测完成", stats_text)
        # 保存日志
        LogHandler.save_log(stats)

    def exit_app(self):
        """退出程序"""
        if self.is_folder_mode and len(self.feedback_records) > 0:
            # 处理未标记的图片
            for record in self.feedback_records:
                if record["feedback"] is None:
                    record["feedback"] = "correct"
            self.show_final_stats()
        self.close()