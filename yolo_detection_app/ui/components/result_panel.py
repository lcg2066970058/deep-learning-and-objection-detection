from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ui.styles import CARD_FRAME, TEXT_EDIT, BTN_PRIMARY, LABEL_TITLE, PRIMARY, SUCCESS, WARNING, PURPLE, apply_shadow


class ResultPanel(QFrame):
    export_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_FRAME)
        self.setMinimumWidth(260)
        self.setMaximumWidth(360)
        apply_shadow(self, blur=15, y_offset=2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("检测结果")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setStyleSheet(LABEL_TITLE)
        layout.addWidget(title)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(TEXT_EDIT)
        self.text_edit.setMinimumHeight(300)
        layout.addWidget(self.text_edit, stretch=1)

        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton("导出 CSV")
        self.btn_export.setStyleSheet(BTN_PRIMARY)
        self.btn_export.setFixedHeight(32)
        self.btn_export.clicked.connect(self.export_requested.emit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_export)
        layout.addLayout(btn_layout)

    def clear(self):
        self.text_edit.clear()

    def set_result(self, img_name: str, total_count: int, boxes, class_names, feedback: str = None):
        html = f"""<html><body style='font-family: Microsoft YaHei; font-size: 12px; color: #1e293b;'>
        <h4 style='color: {PRIMARY}; margin: 0 0 6px 0;'>{img_name}</h4>
        <p style='margin: 2px 0;'><strong>物体数量:</strong> <span style='color: {SUCCESS};'>{total_count}</span></p>
        <hr style='border: 1px solid #e2e8f0; margin: 8px 0;'/>
        """

        if total_count == 0:
            html += "<p style='color: #94a3b8;'>未检测到物体</p>"
        else:
            for idx, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                cls_name = class_names[cls_id]
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                html += f"""
                <p style='margin: 4px 0;'><strong>[{idx+1}]</strong> {cls_name}</p>
                <p style='margin: 1px 0;'>  置信度: <span style='color: {WARNING};'>{conf:.2f}</span></p>
                <p style='margin: 1px 0;'>  坐标: <span style='color: {PURPLE};'>{bbox}</span></p>
                """

        if feedback is not None:
            html += f"<hr style='border: 1px solid #e2e8f0; margin: 8px 0;'/>"
            html += f"<p><strong>反馈:</strong> "
            if feedback == "correct":
                html += f"<span style='color: {SUCCESS};'>已标记正确</span></p>"
            elif feedback == "incorrect":
                html += f"<span style='color: #ef4444;'>已标记错误</span></p>"
            else:
                html += f"<span style='color: {WARNING};'>未标记</span></p>"

        html += "</body></html>"
        self.text_edit.setHtml(html)
