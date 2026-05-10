from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ui.styles import BTN_SUCCESS, BTN_DANGER, BTN_PRIMARY, LABEL_TITLE


class FeedbackBar(QFrame):
    feedback_given = pyqtSignal(str)
    next_requested = pyqtSignal()

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

        self.lbl_progress = QLabel("当前: 0/0 张")
        self.lbl_progress.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.lbl_progress.setStyleSheet(LABEL_TITLE)
        layout.addWidget(self.lbl_progress)

        layout.addStretch()

        self.btn_correct = QPushButton("正确")
        self.btn_correct.setStyleSheet(BTN_SUCCESS)
        self.btn_correct.setFixedSize(100, 36)
        self.btn_correct.clicked.connect(lambda: self.feedback_given.emit("correct"))
        self.btn_correct.setEnabled(False)
        layout.addWidget(self.btn_correct)

        self.btn_incorrect = QPushButton("错误")
        self.btn_incorrect.setStyleSheet(BTN_DANGER)
        self.btn_incorrect.setFixedSize(100, 36)
        self.btn_incorrect.clicked.connect(lambda: self.feedback_given.emit("incorrect"))
        self.btn_incorrect.setEnabled(False)
        layout.addWidget(self.btn_incorrect)

        self.btn_next = QPushButton("下一张")
        self.btn_next.setStyleSheet(BTN_PRIMARY)
        self.btn_next.setFixedSize(100, 36)
        self.btn_next.clicked.connect(self.next_requested.emit)
        self.btn_next.setEnabled(False)
        layout.addWidget(self.btn_next)

        layout.addStretch()

    def set_progress(self, current: int, total: int):
        self.lbl_progress.setText(f"当前: {current}/{total} 张")

    def set_buttons_enabled(self, enabled: bool):
        self.btn_correct.setEnabled(enabled)
        self.btn_incorrect.setEnabled(enabled)
        self.btn_next.setEnabled(enabled)

    def reset_buttons(self):
        self.btn_correct.setEnabled(False)
        self.btn_incorrect.setEnabled(False)
        self.btn_next.setEnabled(False)
        self.btn_correct.setText("正确")
        self.btn_incorrect.setText("错误")
        self.btn_next.setText("下一张")

    def set_feedback_state(self, state: str):
        """state: None, 'correct', 'incorrect'"""
        if state == "correct":
            self.btn_correct.setEnabled(False)
            self.btn_correct.setText("已正确")
            self.btn_incorrect.setEnabled(True)
            self.btn_incorrect.setText("错误")
            self.btn_next.setEnabled(True)
        elif state == "incorrect":
            self.btn_incorrect.setEnabled(False)
            self.btn_incorrect.setText("已错误")
            self.btn_correct.setEnabled(True)
            self.btn_correct.setText("正确")
            self.btn_next.setEnabled(True)
        else:
            self.btn_correct.setEnabled(True)
            self.btn_correct.setText("正确")
            self.btn_incorrect.setEnabled(True)
            self.btn_incorrect.setText("错误")
            self.btn_next.setEnabled(True)
