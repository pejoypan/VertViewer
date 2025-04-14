# mainwindow.py
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QPointF,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QStandardItemModel, QStandardItem,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView, QStackedLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu, QGridLayout,
    QTableView, QToolButton, QVBoxLayout, QWidget, QMainWindow)
from widgets.frame_window import FrameWindow
from threads.image_receiver import ImageReceiverThread
from threads.log_receiver import LogReceiverThread
import utils.log_utils as log_utils
import assets.resources_rc
from widgets.log_table import LogTable
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, image_port="tcp://127.0.0.1:5555", log_port="tcp://127.0.0.1:5556"):
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

        # log receiver
        self.log_receiver_thread = LogReceiverThread(log_port)
        self.log_receiver_thread.log_received.connect(self._update_log)
        self.log_receiver_thread.start()
        
        # image receiver
        self.image_receiver_thread = ImageReceiverThread(image_port)
        self.image_receiver_thread.image_received.connect(self._update_image)
        self.image_receiver_thread.start()

        # log table
        self.ui.left_part.layout().removeWidget(self.ui.widget_log_control)
        stacked_layout = QStackedLayout(self.ui.log_widget)
        stacked_layout.setStackingMode(QStackedLayout.StackAll)
        stacked_layout.addWidget(self.ui.widget_log_control)
        stacked_layout.setAlignment(self.ui.widget_log_control, Qt.AlignTop)
        self.log_table = LogTable(self, clear_btn=self.ui.button_clear_log, export_btn=self.ui.button_log_export, filter_btn=self.ui.button_log_filter)
        stacked_layout.addWidget(self.log_table)


    @Slot(str, int, QImage)
    def _update_image(self, device_id, frame_id, qimg):
        self.frame_window._update_image(device_id, frame_id, qimg)

    @Slot(str)
    def _update_log(self, zmqmsg):
        result = log_utils.parse_log_line(zmqmsg)
        if result:
            self.log_table._append_log(*result)
        self.log_table.scrollToBottom()

    def closeEvent(self, event):
        print("关闭窗口，退出线程")
        self.image_receiver_thread.requestInterruption()
        self.image_receiver_thread.quit()
        self.image_receiver_thread.wait()
        self.log_receiver_thread.requestInterruption()
        self.log_receiver_thread.quit()
        self.log_receiver_thread.wait()
        print("线程退出完毕")
        event.accept()
