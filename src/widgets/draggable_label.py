from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QScrollArea

class DraggableLabel(QLabel):

    def __init__(self, parent, scroll_area: QScrollArea, zoom_callback=None):
        super().__init__(parent)
        self.scroll_area = scroll_area
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setScaledContents(True)
        self._drag_start = None
        self._h_scroll_start = None
        self._v_scroll_start = None

        self.zoom_callback = zoom_callback

    def wheelEvent(self, event):
        if self.zoom_callback:
            delta = event.angleDelta().y()
            factor = 1.111 if delta > 0 else 0.9
            self.zoom_callback(factor) 
        event.accept()

    def mousePressEvent(self, event):
        self.update()
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPosition()
            self._h_scroll_start = self.scroll_area.horizontalScrollBar().value()
            self._v_scroll_start = self.scroll_area.verticalScrollBar().value()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            delta = event.globalPosition() - self._drag_start
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            h_bar.setValue(self._h_scroll_start - delta.x())
            v_bar.setValue(self._v_scroll_start - delta.y())
            event.accept()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.unsetCursor()
            event.accept()
        else:
            super().mouseReleaseEvent(event)