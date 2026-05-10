from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ui.styles import LABEL_MUTED


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-top: 1px solid #e2e8f0;
                padding: 4px 12px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(20)

        self.lbl_model = QLabel("模型: 未加载")
        self.lbl_device = QLabel("设备: CPU")
        self.lbl_status = QLabel("就绪")
        self.lbl_fps = QLabel("")

        for lbl in (self.lbl_model, self.lbl_device, self.lbl_status, self.lbl_fps):
            lbl.setStyleSheet(LABEL_MUTED)
            lbl.setFont(QFont("Microsoft YaHei", 10))

        layout.addWidget(self.lbl_model)
        layout.addWidget(self.lbl_device)
        layout.addStretch()
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.lbl_fps)

    def set_model(self, name: str):
        self.lbl_model.setText(f"模型: {name}")

    def set_device(self, device: str):
        self.lbl_device.setText(f"设备: {device}")

    def set_status(self, text: str):
        self.lbl_status.setText(text)

    def set_fps(self, fps: float):
        if fps > 0:
            self.lbl_fps.setText(f"FPS: {fps:.1f}")
        else:
            self.lbl_fps.setText("")
