import cv2
import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QWheelEvent, QMouseEvent
from PyQt5.QtCore import Qt, QPointF

from ui.styles import CARD_FRAME, apply_shadow


class ImageViewer(QGraphicsView):
    """Custom image viewer with zoom (wheel) and pan (drag) support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        # 使用整数常量 2（Qt.SmoothTransformation 的值）
        self._pixmap_item.setTransformationMode(2)
        self._scene.addItem(self._pixmap_item)

        # 设置渲染提示（使用整数常量，兼容所有版本的PyQt5）
        # Qt.Antialiasing = 1, Qt.SmoothTransformation = 2
        render_hints = self.renderHints() | 1 | 2
        self.setRenderHints(render_hints)

        self.setStyleSheet(CARD_FRAME)
        self.setFrameShape(QGraphicsView.NoFrame)
        apply_shadow(self, blur=15, y_offset=2)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setAlignment(Qt.AlignCenter)

        self._zoom = 0
        self._empty = True
        self._drag_start = None

    def set_image(self, image):
        """
        Set image from numpy array (BGR/RGB) or QPixmap.
        :param image: np.ndarray or QPixmap or None
        """
        if image is None:
            self._empty = True
            self._pixmap_item.setPixmap(QPixmap())
            self._scene.setSceneRect(0, 0, 0, 0)
            return

        if isinstance(image, np.ndarray):
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            h, w, ch = image.shape
            bytes_per_line = ch * w
            qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
        elif isinstance(image, QPixmap):
            pixmap = image
        else:
            raise TypeError("image must be np.ndarray or QPixmap")

        self._empty = False
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(self._pixmap_item.boundingRect())
        self.fit_in_view()

    def fit_in_view(self):
        """Fit the image into the viewport while keeping aspect ratio."""
        if self._empty:
            return
        self._zoom = 0
        self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        if self._empty:
            return

        # Zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
            self._zoom += 1
        else:
            factor = zoom_out_factor
            self._zoom -= 1

        self.scale(factor, factor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and not self._empty:
            self._drag_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_start is not None and not self._empty:
            delta = event.pos() - self._drag_start
            self._drag_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if not self._empty:
            self.fit_in_view()
        super().mouseDoubleClickEvent(event)

    def reset_view(self):
        self.fit_in_view()

    def is_empty(self):
        return self._empty
