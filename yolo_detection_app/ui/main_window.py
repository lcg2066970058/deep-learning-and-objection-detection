import sys
import csv
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QApplication, QMenuBar
)
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtCore import Qt, QThread

from config.settings import (
    BASE_DIR, EXPORT_DIR, LOG_DIR, SUPPORT_IMG_SUFFIX,
    APP_NAME, APP_VERSION, MODEL_PATH
)
from model.detector import YoloDetector
from utils.log_handler import LogHandler
from utils.path_utils import save_last_path, load_last_path
from ui.styles import PRIMARY, SUCCESS, DANGER, LABEL_TITLE, apply_shadow

from ui.components.image_viewer import ImageViewer
from ui.components.result_panel import ResultPanel
from ui.components.control_bar import ControlBar
from ui.components.feedback_bar import FeedbackBar
from ui.components.sidebar import Sidebar
from ui.components.status_bar import StatusBar
from ui.workers import CameraWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1300, 800)
        self.setMinimumSize(1000, 650)

        # Init detector
        try:
            self.detector = YoloDetector()
        except Exception as e:
            QMessageBox.critical(self, "模型加载失败", str(e))
            sys.exit(1)

        # State
        self.img_list = []
        self.current_index = -1
        self.current_results = None
        self.feedback_records = []
        self.is_folder_mode = False
        self.camera_active = False
        self.camera_worker = None
        self.current_conf = None  # None means use default

        # UI setup - 必须先创建UI组件，再绑定菜单信号
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._setup_shortcuts()
        self._update_status_bar()

    def _setup_menu(self):
        menubar = self.menuBar()
        # File menu
        file_menu = menubar.addMenu("文件(F)")

        act_open = file_menu.addAction("打开图片...")
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self._on_open_image)

        act_folder = file_menu.addAction("打开文件夹...")
        act_folder.setShortcut(QKeySequence("Ctrl+Shift+O"))
        act_folder.triggered.connect(self._on_open_folder)

        file_menu.addSeparator()

        act_export = file_menu.addAction("导出结果")
        act_export.setShortcut(QKeySequence("Ctrl+E"))
        act_export.triggered.connect(self._on_export)

        file_menu.addSeparator()

        act_exit = file_menu.addAction("退出")
        act_exit.setShortcut(QKeySequence("Alt+F4"))
        act_exit.triggered.connect(self.close)

        # View menu
        view_menu = menubar.addMenu("视图(V)")
        act_fit = view_menu.addAction("适应窗口")
        act_fit.setShortcut(QKeySequence("Ctrl+0"))
        act_fit.triggered.connect(self.image_viewer.fit_in_view)

        act_reset = view_menu.addAction("重置缩放")
        act_reset.setShortcut(QKeySequence("Ctrl+R"))
        act_reset.triggered.connect(self.image_viewer.reset_view)

        # Help menu
        help_menu = menubar.addMenu("帮助(H)")
        act_about = help_menu.addAction("关于")
        act_about.triggered.connect(self._show_about)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background-color: #f8fafc;")

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 1. Control bar
        self.control_bar = ControlBar()
        main_layout.addWidget(self.control_bar)

        # 2. Content area (sidebar + image + result)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # 2.1 Sidebar
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)

        # 2.2 Image viewer
        self.image_viewer = ImageViewer()
        content_layout.addWidget(self.image_viewer, stretch=3)

        # 2.3 Result panel
        self.result_panel = ResultPanel()
        content_layout.addWidget(self.result_panel, stretch=1)

        main_layout.addLayout(content_layout, stretch=1)

        # 3. Feedback bar
        self.feedback_bar = FeedbackBar()
        main_layout.addWidget(self.feedback_bar)

        # 4. Status bar
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)

    def _connect_signals(self):
        self.control_bar.open_image.connect(self._on_open_image)
        self.control_bar.open_folder.connect(self._on_open_folder)
        self.control_bar.toggle_camera.connect(self._on_toggle_camera)
        self.control_bar.conf_changed.connect(self._on_conf_changed)
        self.control_bar.export_all.connect(self._on_export)

        self.feedback_bar.feedback_given.connect(self._on_feedback)
        self.feedback_bar.next_requested.connect(self._show_next_image)

        self.result_panel.export_requested.connect(self._on_export)

        self.sidebar.item_clicked.connect(self._on_sidebar_item_clicked)

    def _setup_shortcuts(self):
        # Navigation
        self.shortcut_prev = QKeySequence("Left")
        # We handle shortcuts via keyPressEvent for simplicity with repeated keys

    def keyPressEvent(self, event):
        if self.camera_active:
            if event.key() == Qt.Key_Escape:
                self._stop_camera()
            return

        key = event.key()
        if key in (Qt.Key_A, Qt.Key_Left):
            self._show_prev_image()
        elif key in (Qt.Key_D, Qt.Key_Right, Qt.Key_Space):
            self._show_next_image()
        elif key == Qt.Key_C:
            if self.feedback_bar.btn_correct.isEnabled():
                self._on_feedback("correct")
        elif key == Qt.Key_X:
            if self.feedback_bar.btn_incorrect.isEnabled():
                self._on_feedback("incorrect")
        elif key == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _update_status_bar(self):
        self.status_bar.set_model(MODEL_PATH.name)
        import torch
        device = "CUDA" if torch.cuda.is_available() else "CPU"
        self.status_bar.set_device(device)
        self.status_bar.set_status("就绪")

    # ------------------------------------------------------------------
    # Open image / folder
    # ------------------------------------------------------------------
    def _on_open_image(self):
        self._stop_camera()
        self._reset_state()
        self.is_folder_mode = False

        # 获取上次打开的路径作为默认路径
        last_path = load_last_path()
        # 如果上次路径是文件夹，使用它；如果是文件，使用它的父目录
        default_path = ""
        if last_path:
            p = Path(last_path)
            if p.is_file():
                default_path = str(p.parent)
            elif p.is_dir():
                default_path = last_path

        suffix_filter = " ".join(SUPPORT_IMG_SUFFIX)
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", default_path, f"图片文件 ({suffix_filter})"
        )
        if file_path:
            # 保存当前路径供下次使用
            save_last_path(file_path)
            self.img_list = [Path(file_path)]
            self.current_index = 0
            self.sidebar.set_images(self.img_list)
            self.sidebar.set_current_index(0)
            self._detect_and_show()
            self._update_btn_state()
            self.feedback_bar.set_progress(1, 1)

    def _on_open_folder(self):
        self._stop_camera()
        self._reset_state()
        self.is_folder_mode = True

        # 获取上次打开的路径作为默认路径
        last_path = load_last_path()
        # 如果上次路径是文件夹，使用它；如果是文件，使用它的父目录
        default_path = ""
        if last_path:
            p = Path(last_path)
            if p.is_file():
                default_path = str(p.parent)
            elif p.is_dir():
                default_path = last_path

        folder_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹", default_path)
        if not folder_path:
            return

        folder = Path(folder_path)
        # 保存当前路径供下次使用
        save_last_path(folder_path)
        
        for suffix in SUPPORT_IMG_SUFFIX:
            self.img_list.extend(list(folder.glob(suffix)))
        self.img_list.sort()

        if len(self.img_list) == 0:
            QMessageBox.warning(self, "提示", "文件夹内未找到支持的图片文件！")
            return

        self.feedback_records = [{"img_path": img, "feedback": None} for img in self.img_list]
        self.current_index = 0
        self.sidebar.set_images(self.img_list)
        self.sidebar.set_current_index(0)
        self._detect_and_show()
        self._update_btn_state()
        self.feedback_bar.set_progress(1, len(self.img_list))

    def _reset_state(self):
        self._stop_camera()
        self.img_list = []
        self.current_index = -1
        self.current_results = None
        self.feedback_records = []
        self.is_folder_mode = False
        self.image_viewer.set_image(None)
        self.result_panel.clear()
        self.feedback_bar.set_progress(0, 0)
        self.feedback_bar.reset_buttons()
        self.sidebar.clear()
        self.setWindowTitle(APP_NAME)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------
    def _detect_and_show(self):
        if self.current_index < 0 or self.current_index >= len(self.img_list):
            return

        self.status_bar.set_status("检测中...")
        QApplication.processEvents()

        img_path = self.img_list[self.current_index]
        self.setWindowTitle(f"{APP_NAME} - {img_path.name}")

        try:
            self.current_results = self.detector.detect_image(img_path, conf=self.current_conf)
        except Exception as e:
            QMessageBox.critical(self, "检测失败", str(e))
            self.status_bar.set_status("检测失败")
            return

        annotated = self.current_results.plot()
        # 直接传入 BGR 格式，set_image 会自动转换
        self.image_viewer.set_image(annotated)

        self._update_result_text()
        self._reset_feedback_btn()
        self.sidebar.set_current_index(self.current_index)
        self.status_bar.set_status("就绪")

    def _update_result_text(self):
        if self.current_results is None:
            return

        img_name = self.img_list[self.current_index].name
        total = len(self.current_results.boxes)
        feedback = None
        if self.is_folder_mode and 0 <= self.current_index < len(self.feedback_records):
            feedback = self.feedback_records[self.current_index]["feedback"]

        self.result_panel.set_result(
            img_name=img_name,
            total_count=total,
            boxes=self.current_results.boxes,
            class_names=self.detector.class_names,
            feedback=feedback
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _show_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._detect_and_show()
            self._update_btn_state()
            self.feedback_bar.set_progress(self.current_index + 1, len(self.img_list))

    def _show_next_image(self):
        if not self.is_folder_mode and len(self.img_list) == 1:
            return
        if self.current_index == len(self.img_list) - 1 and self.is_folder_mode:
            self._show_final_stats()
            return
        if self.current_index < len(self.img_list) - 1:
            self.current_index += 1
            self._detect_and_show()
            self._update_btn_state()
            self.feedback_bar.set_progress(self.current_index + 1, len(self.img_list))

    def _update_btn_state(self):
        has_images = len(self.img_list) > 0
        # Navigation handled by shortcuts; update progress only

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------
    def _on_feedback(self, feedback_type):
        if not self.is_folder_mode or self.current_index < 0:
            return
        self.feedback_records[self.current_index]["feedback"] = feedback_type
        self.sidebar.set_feedback(self.current_index, feedback_type)
        self._reset_feedback_btn()
        self._update_result_text()

    def _reset_feedback_btn(self):
        if not self.is_folder_mode:
            self.feedback_bar.set_buttons_enabled(False)
            return

        fb = self.feedback_records[self.current_index]["feedback"]
        self.feedback_bar.set_feedback_state(fb)

    # ------------------------------------------------------------------
    # Final stats
    # ------------------------------------------------------------------
    def _show_final_stats(self):
        stats = LogHandler.calculate_stats(self.feedback_records)
        if not stats:
            return

        LogHandler.print_stats_to_console(stats)

        html = (
            f"<html><body style='font-family: Microsoft YaHei; font-size: 13px;'>"
            f"<h3 style='color: {PRIMARY};'>检测完成</h3>"
            f"<p>总数: <strong style='color: {PRIMARY};'>{stats['total']}</strong> 张</p>"
            f"<p>已检测: <strong style='color: {PRIMARY};'>{stats['detected']}</strong> 张</p>"
            f"<p>检测率: <strong style='color: {PRIMARY};'>{stats['detection_rate']:.2f}%</strong></p>"
            f"<p>正确: <strong style='color: {SUCCESS};'>{stats['correct']}</strong> 张</p>"
            f"<p>错误: <strong style='color: {DANGER};'>{stats['incorrect']}</strong> 张</p>"
            f"<p>正确率: <strong style='color: {SUCCESS};'>{stats['accuracy']:.2f}%</strong></p>"
            f"<p>错误率: <strong style='color: {DANGER};'>{stats['error_rate']:.2f}%</strong></p>"
            f"</body></html>"
        )
        QMessageBox.information(self, "检测统计", html)
        LogHandler.save_log(stats)

    # ------------------------------------------------------------------
    # Sidebar click
    # ------------------------------------------------------------------
    def _on_sidebar_item_clicked(self, index):
        if 0 <= index < len(self.img_list):
            self.current_index = index
            self._detect_and_show()
            self._update_btn_state()
            self.feedback_bar.set_progress(self.current_index + 1, len(self.img_list))

    # ------------------------------------------------------------------
    # Confidence changed
    # ------------------------------------------------------------------
    def _on_conf_changed(self, conf):
        self.current_conf = conf
        if self.current_index >= 0 and not self.camera_active:
            self._detect_and_show()

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------
    def _on_toggle_camera(self):
        if self.camera_active:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        self._reset_state()
        self.camera_active = True
        self.control_bar.set_camera_active(True)
        self.status_bar.set_status("摄像头运行中")
        self.image_viewer.set_image(None)
        self.result_panel.clear()

        self.camera_worker = CameraWorker(
            self.detector,
            conf=self.current_conf,
            fps=30
        )
        self.camera_worker.frame_ready.connect(self._on_camera_frame)
        self.camera_worker.fps_updated.connect(self._on_camera_fps)
        self.camera_worker.error_occurred.connect(self._on_camera_error)
        self.camera_worker.start()

    def _stop_camera(self):
        if self.camera_worker:
            self.camera_worker.stop()
            self.camera_worker = None
        self.camera_active = False
        self.control_bar.set_camera_active(False)
        self.status_bar.set_fps(0)
        self.status_bar.set_status("就绪")
        # 清除摄像头画面，避免停留在最后一帧
        self.image_viewer.set_image(None)
        self.result_panel.clear()

    def _on_camera_frame(self, frame):
        self.image_viewer.set_image(frame)
        # Optionally show detection count in result panel
        self.result_panel.text_edit.setHtml(
            "<p style='color: #94a3b8;'>实时摄像头模式 - 按 ESC 退出</p>"
        )

    def _on_camera_fps(self, fps):
        self.status_bar.set_fps(fps)

    def _on_camera_error(self, msg):
        QMessageBox.critical(self, "摄像头错误", msg)
        self._stop_camera()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def _on_export(self):
        if not self.current_results or self.camera_active:
            QMessageBox.information(self, "提示", "没有可导出的检测结果")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = EXPORT_DIR / f"detection_results_{timestamp}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["文件名", "序号", "类别", "置信度", "x1", "y1", "x2", "y2"])

            for idx, box in enumerate(self.current_results.boxes):
                cls_id = int(box.cls[0])
                cls_name = self.detector.class_names[cls_id]
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                writer.writerow([
                    self.img_list[self.current_index].name,
                    idx + 1,
                    cls_name,
                    f"{conf:.4f}",
                    bbox[0], bbox[1], bbox[2], bbox[3]
                ])

        QMessageBox.information(self, "导出成功", f"结果已保存到:\n{csv_path}")

    # ------------------------------------------------------------------
    # About
    # ------------------------------------------------------------------
    def _show_about(self):
        QMessageBox.about(
            self, "关于",
            f"<h3>{APP_NAME}</h3>"
            f"<p>版本: {APP_VERSION}</p>"
            f"<p>基于 YOLOv8 的目标检测工具</p>"
        )

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._stop_camera()
        if self.is_folder_mode and len(self.feedback_records) > 0:
            self._show_final_stats()
        event.accept()
