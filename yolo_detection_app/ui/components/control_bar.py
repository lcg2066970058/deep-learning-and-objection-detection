from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QSlider, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from config.settings import SUPPORT_IMG_SUFFIX
from ui.styles import BTN_PRIMARY, BTN_SUCCESS, BTN_SECONDARY, SLIDER, LABEL_TITLE, LABEL_MUTED


class ControlBar(QFrame):
    open_image = pyqtSignal()
    open_folder = pyqtSignal()
    toggle_camera = pyqtSignal()
    conf_changed = pyqtSignal(float)
    export_all = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # File buttons
        self.btn_open = QPushButton("打开图片")
        self.btn_open.setStyleSheet(BTN_PRIMARY)
        self.btn_open.setFixedHeight(32)
        self.btn_open.clicked.connect(self.open_image.emit)
        layout.addWidget(self.btn_open)

        self.btn_folder = QPushButton("打开文件夹")
        self.btn_folder.setStyleSheet(BTN_PRIMARY)
        self.btn_folder.setFixedHeight(32)
        self.btn_folder.clicked.connect(self.open_folder.emit)
        layout.addWidget(self.btn_folder)

        # Camera button
        self.btn_camera = QPushButton("开启摄像头")
        self.btn_camera.setStyleSheet(BTN_SUCCESS)
        self.btn_camera.setFixedHeight(32)
        self.btn_camera.setCheckable(True)
        self.btn_camera.clicked.connect(self._on_camera_toggle)
        layout.addWidget(self.btn_camera)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Confidence slider
        lbl_conf = QLabel("置信度:")
        lbl_conf.setStyleSheet(LABEL_TITLE)
        lbl_conf.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        layout.addWidget(lbl_conf)

        self.slider_conf = QSlider(Qt.Horizontal)
        self.slider_conf.setStyleSheet(SLIDER)
        self.slider_conf.setMinimum(10)
        self.slider_conf.setMaximum(95)
        self.slider_conf.setValue(50)
        self.slider_conf.setFixedWidth(140)
        self.slider_conf.valueChanged.connect(self._on_conf_changed)
        layout.addWidget(self.slider_conf)

        self.lbl_conf_value = QLabel("0.50")
        self.lbl_conf_value.setStyleSheet(LABEL_MUTED)
        self.lbl_conf_value.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(self.lbl_conf_value)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Export button
        self.btn_export = QPushButton("导出全部")
        self.btn_export.setStyleSheet(BTN_SECONDARY)
        self.btn_export.setFixedHeight(32)
        self.btn_export.clicked.connect(self.export_all.emit)
        layout.addWidget(self.btn_export)

    def _on_conf_changed(self, value):
        conf = value / 100.0
        self.lbl_conf_value.setText(f"{conf:.2f}")
        self.conf_changed.emit(conf)

    def _on_camera_toggle(self, checked):
        if checked:
            self.btn_camera.setText("关闭摄像头")
        else:
            self.btn_camera.setText("开启摄像头")
        self.toggle_camera.emit()

    def get_conf(self) -> float:
        return self.slider_conf.value() / 100.0

    def set_camera_active(self, active: bool):
        self.btn_camera.setChecked(active)
        self.btn_camera.setText("关闭摄像头" if active else "开启摄像头")
