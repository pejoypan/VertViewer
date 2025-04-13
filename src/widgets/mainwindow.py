# mainwindow.py
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QPointF,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QStandardItemModel, QStandardItem,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu, QGridLayout,
    QTableView, QToolButton, QVBoxLayout, QWidget, QMainWindow)
from widgets.frame_window import FrameWindow
from threads.image_receiver import ImageReceiverThread
from threads.log_receiver import LogReceiverThread
import utils.log_utils as log_utils
import assets.resources_rc
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, image_port="tcp://127.0.0.1:5555", log_port="tcp://127.0.0.1:5556"):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.MAX_LOG_LINES = 10

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

        # log model TODO: 1. export to csv 2. clear up 3. filter
        self.log_model = QStandardItemModel(0, 4, self)
        self.log_model.setHorizontalHeaderLabels(["Time", "Level", "Source", "Detail"])
        self.ui.tableView.setModel(self.log_model)

        self.ui.tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.tableView.verticalHeader().setVisible(False)
        self.ui.tableView.setAlternatingRowColors(True)
        self.ui.tableView.setColumnWidth(0, 155)   # time
        self.ui.tableView.setColumnWidth(1, 85)   # level
        self.ui.tableView.setColumnWidth(2, 60)  # source


    @Slot(str, int, QImage)
    def _update_image(self, device_id, frame_id, qimg):
        self.frame_window._update_image(device_id, frame_id, qimg)

    @Slot(str)
    def _update_log(self, msg):
        result = log_utils.parse_log_line(msg)
        if result:
            time, level, source, detail = result
            emoji = log_utils.get_emoji(level)
            row = [
                QStandardItem(time),
                QStandardItem(f"{emoji} {level}"),
                QStandardItem(source),
                QStandardItem(detail),
            ]
            emoji = log_utils.get_emoji(level)
            for item in row:
                item.setEditable(False)
            if self.log_model.rowCount() >= self.MAX_LOG_LINES:
                self.log_model.removeRow(self.log_model.rowCount() - 1)
            self.log_model.insertRow(0, row)

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
