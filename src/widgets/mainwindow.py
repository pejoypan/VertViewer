# mainwindow.py
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QPointF,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu, QGridLayout,
    QTableView, QToolButton, QVBoxLayout, QWidget, QMainWindow)
from widgets.frame_window import FrameWindow
from threads.receiver import ImageReceiverThread
import assets.resources_rc
from ui.ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, port="tcp://127.0.0.1:5555"):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.frame_layout = QGridLayout()
        self.frame_windows = QWidget(self)
        self.frame_windows.setLayout(self.frame_layout)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(8)

        size_hint = (320, 280)
        scale_hint = 0.3125
    

        self.frame_window = FrameWindow(size_hint, scale_hint)
        self.frame_layout.addWidget(self.frame_window, 0, 0)

        # FIXME: just for test
        fwin1 = FrameWindow(size_hint, scale_hint)
        self.frame_layout.addWidget(fwin1, 0, 1)
        fwin2 = FrameWindow(size_hint, scale_hint)
        self.frame_layout.addWidget(fwin2, 0, 2)
        fwin3 = FrameWindow(size_hint, scale_hint)
        self.frame_layout.addWidget(fwin3, 1, 0)
        fwin4 = FrameWindow(size_hint, scale_hint)
        self.frame_layout.addWidget(fwin4, 1, 1)
        fwin5 = FrameWindow(size_hint, scale_hint)
        self.frame_layout.addWidget(fwin5, 1, 2)
        # FIXME

        self.ui.scrollArea.setWidget(self.frame_windows)    
        

        self.receiver_thread = ImageReceiverThread(port)
        self.receiver_thread.image_received.connect(self._update_image)
        self.receiver_thread.start()
    

    @Slot(str, int, QImage)
    def _update_image(self, device_id, frame_id, qimg):
        self.frame_window._update_image(device_id, frame_id, qimg)


    def closeEvent(self, event):
        print("关闭窗口，退出线程")
        self.receiver_thread.requestInterruption()
        self.receiver_thread.quit()
        self.receiver_thread.wait()
        print("线程退出完毕")
        event.accept()
