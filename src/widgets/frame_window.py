# frame_window.py
import time
from pathlib import Path
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QPointF,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QRegion,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu, QStackedLayout,
    QTableView, QToolButton, QVBoxLayout, QWidget)
from ui.ui_frame import Ui_Frame
from widgets.draggable_label import DraggableLabel
import utils.time_utils as time_utils

class FrameWindow(QWidget):
    def __init__(self, user_id, size_hint=(512, 512), scale_hint=0.5):
        super().__init__()
        self.ui = Ui_Frame()
        self.ui.setupUi(self)

        self.user_id = user_id
        self.ui.label_user_id.setText(str(user_id))


        self.image_label = DraggableLabel(self, self.ui.scrollArea, zoom_callback=self._zoom_by_wheel)
        self.image_label.resize(size_hint[0], size_hint[1])
        self._scale_factor = scale_hint
        self.ui.scrollArea.setWidget(self.image_label)
        margin = self.ui.scrollArea.frameWidth() * 2
        self.ui.scrollArea.setFixedSize(size_hint[0] + margin, size_hint[1] + margin)
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.ui.verticalLayout.removeWidget(self.ui.horizontalWidget)
        self.ui.verticalLayout.removeWidget(self.ui.scrollArea)

        overlay_container = QWidget(self)
        stacked_layout = QStackedLayout(overlay_container)
        stacked_layout.setStackingMode(QStackedLayout.StackAll)


        stacked_layout.addWidget(self.ui.horizontalWidget)
        stacked_layout.setAlignment(self.ui.horizontalWidget, Qt.AlignTop)
        stacked_layout.addWidget(self.ui.scrollArea)

        self.ui.verticalLayout.insertWidget(0, overlay_container)


        # fps timer
        self.fps_frame_count = 0
        self.last_fps_time = time.time()
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self._update_fps)
        self.fps_timer.start(1000)

        menu = QMenu(self)

        self.zoom_in_act = menu.addAction("Zoom In")
        self.zoom_in_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn)))
        self.zoom_in_act.triggered.connect(self._zoom_in)

        self.zoom_out_act = menu.addAction("Zoom Out")
        self.zoom_out_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomOut)))
        self.zoom_out_act.triggered.connect(self._zoom_out)

        self.zoom_fit_act = menu.addAction("Zoom Fit")
        self.zoom_fit_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomFitBest)))
        self.zoom_fit_act.triggered.connect(self._zoom_fit)

        menu.addSeparator()

        self.save_act = menu.addAction("Save")
        self.save_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave)))
        self.save_act.triggered.connect(self._save_current_image)

        self.ui.toolButton.setMenu(menu)


    @Slot(str, int, QImage, int)
    def _update_image(self, device_id, frame_id, qimg, err_count):
        self.image_label.setPixmap(QPixmap.fromImage(qimg))
        self.ui.label_id.setText(str(frame_id))
        self.ui.label_error.setText(str(err_count))
        self.fps_frame_count += 1

    @Slot()
    def _update_fps(self):
        now = time.time()
        elapsed = now - self.last_fps_time
        if elapsed > 0:
            fps = self.fps_frame_count / elapsed
            self.ui.label_fps.setText(f"{fps:.1f} fps")
        self.fps_frame_count = 0
        self.last_fps_time = now

    @Slot()
    def _save_current_image(self):
        if not self.image_label.pixmap():
            return

        pixmap = self.image_label.pixmap()
        qimage = pixmap.toImage()

        pictures_path = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)

        filename = f"{self.ui.label_user_id.text()}_{self.ui.label_id.text()}_{time_utils.now_time()}.png"
        save_path = Path(pictures_path) / filename
        save_path = save_path.as_posix()
        
        if not qimage.save(save_path):
            QMessageBox.critical(self, "Error", "Failed to save image")
        else:
            QMessageBox.information(self, "Success", f"Image saved to\n{save_path}")

    def _scale_image(self, factor):
        self._scale_factor *= factor

        new_size = self._scale_factor * self.image_label.pixmap().size()
        self.image_label.resize(new_size)

        self._adjust_scrollbar(self.ui.scrollArea.horizontalScrollBar(), factor)
        self._adjust_scrollbar(self.ui.scrollArea.verticalScrollBar(), factor)


    def _adjust_scrollbar(self, scrollBar, factor):
        pos = int(factor * scrollBar.value()
                  + ((factor - 1) * scrollBar.pageStep() / 2))
        scrollBar.setValue(pos)

    @Slot()
    def _zoom_in(self):
        if not self.image_label.pixmap():
            return
        self._scale_image(1.25)

    @Slot()
    def _zoom_out(self):
        if not self.image_label.pixmap():
            return
        self._scale_image(0.80)

    @Slot()
    def _zoom_fit(self):
        if not self.image_label.pixmap():
            return

        window_w = self.ui.scrollArea.width() - 2
        window_h = self.ui.scrollArea.height() - 2
        image_w = self.image_label.pixmap().width()
        image_h = self.image_label.pixmap().height()

        ratio_w = window_w / image_w
        ratio_h = window_h / image_h

        ratio = ratio_w if ratio_w < ratio_h else ratio_h
        new_size = ratio * self.image_label.pixmap().size()

        self.image_label.resize(new_size)
        self._scale_factor = ratio

    def _zoom_by_wheel(self, factor):
        if not self.image_label.pixmap():
            return

        self._scale_image(factor)