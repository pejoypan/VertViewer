# main.py
import time
from pathlib import Path
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu,
    QTableView, QToolButton, QVBoxLayout, QWidget)
from threads.receiver import ImageReceiverThread
from ui.ui_frame import Ui_Frame
import utils.time_utils as time_utils

class FrameWindow(QWidget): # TODO: just for test now, should change to Mainwindow
    def __init__(self):
        super().__init__()
        self.ui = Ui_Frame()
        self.ui.setupUi(self)

        self.setWindowTitle("ZeroMQ Image Viewer")

        self.image_label = QLabel("Waiting for image...", self)
        self.ui.scrollArea.setWidget(self.image_label)

        self.fps_frame_count = 0
        self.last_fps_time = time.time()

        # fps timer
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self._update_fps)
        self.fps_timer.start(1000)

        self.receiver_thread = ImageReceiverThread("tcp://127.0.0.1:5555")
        self.receiver_thread.image_received.connect(self._update_image)
        self.receiver_thread.start()

        self.ui.pushButton.toggled.connect(self._on_toggle_recv)

        menu = QMenu(self)

        self.zoom_in_act = menu.addAction("Zoom In")
        self.zoom_in_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn)))

        self.zoom_out_act = menu.addAction("Zoom Out")
        self.zoom_out_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomOut)))

        self.zoom_fit_act = menu.addAction("Zoom Fit")
        self.zoom_fit_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomFitBest)))

        menu.addSeparator()

        self.save_act = menu.addAction("Save")
        self.save_act.setIcon(QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave)))
        self.save_act.triggered.connect(self._save_current_image)

        self.ui.toolButton.setMenu(menu)


    @Slot(str, int, QImage)
    def _update_image(self, device_id, frame_id, qimg):
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation # or FastTransformation
        )
        self.image_label.setPixmap(pixmap)
        self.ui.label_user_id.setText(str(device_id))
        self.ui.label_id.setText(str(frame_id))
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

    @Slot(bool)
    def _on_toggle_recv(self, checked):
        self.receiver_thread.set_paused(not checked)

    @Slot()
    def _save_current_image(self):
        if not self.image_label.pixmap():
            return

        pixmap = self.image_label.pixmap()
        qimage = pixmap.toImage()

        pictures_path = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)

        filename = f"{self.ui.label_user_id.text()}_{self.ui.label_id.text()}_{time_utils.now_time()}.png"
        save_path = Path(pictures_path) / filename #  os.path.join(pictures_path, filename)
        save_path = save_path.as_posix()
        print(f"save_path: {save_path}")
        if not qimage.save(save_path):
            QMessageBox.critical(self, "Error", "Failed to save image")
        else:
            QMessageBox.information(self, "Success", f"Image saved to\n{save_path}")


    def closeEvent(self, event):
        print("关闭窗口，退出线程")
        self.receiver_thread.requestInterruption()
        self.receiver_thread.quit()
        self.receiver_thread.wait()
        print("线程退出完毕")
        event.accept()


import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrameWindow()
    window.show()
    sys.exit(app.exec())