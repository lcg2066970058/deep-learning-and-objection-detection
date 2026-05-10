from pathlib import Path
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ui.styles import SIDEBAR_FRAME, LIST_WIDGET, LABEL_TITLE, SUCCESS, DANGER, TEXT_PRIMARY


class Sidebar(QFrame):
    item_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(SIDEBAR_FRAME)
        self.setMinimumWidth(180)
        self.setMaximumWidth(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("文件列表")
        title.setStyleSheet(LABEL_TITLE)
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(LIST_WIDGET)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        self._img_list = []
        self._feedback_map = {}

    def set_images(self, img_list: list[Path]):
        self._img_list = img_list
        self._feedback_map = {}
        self.list_widget.clear()
        for idx, path in enumerate(img_list):
            item = QListWidgetItem(path.name)
            item.setData(Qt.UserRole, idx)
            self.list_widget.addItem(item)

    def set_feedback(self, index: int, feedback: str):
        self._feedback_map[index] = feedback
        item = self.list_widget.item(index)
        if item is None:
            return
        name = self._img_list[index].name
        if feedback == "correct":
            item.setText(f"[OK] {name}")
            item.setForeground(Qt.green)
        elif feedback == "incorrect":
            item.setText(f"[NG] {name}")
            item.setForeground(Qt.red)
        else:
            item.setText(name)
            item.setForeground(Qt.black)

    def set_current_index(self, index: int):
        if 0 <= index < self.list_widget.count():
            self.list_widget.setCurrentRow(index)

    def _on_item_clicked(self, item: QListWidgetItem):
        idx = item.data(Qt.UserRole)
        self.item_clicked.emit(idx)

    def clear(self):
        self._img_list = []
        self._feedback_map = {}
        self.list_widget.clear()
