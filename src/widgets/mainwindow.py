# mainwindow.py
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QPointF,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QStandardItemModel, QStandardItem,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView, QStackedLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu, QGridLayout, QSpacerItem,
    QTableView, QToolButton, QVBoxLayout, QWidget, QMainWindow)
from widgets.frame_window import FrameWindow
from threads.image_receiver import ImageReceiverThread
from threads.log_receiver import LogReceiverThread
import utils.log_utils as log_utils
import utils.time_utils as time_utils
import assets.resources_rc
from widgets.log_table import LogTable
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fixed_size = kwargs.get("size", (1920, 1080))
        self.setFixedSize(self.fixed_size[0], self.fixed_size[1])

        # log table
        self.log_table = LogTable(self, clear_btn=self.ui.button_clear_log, export_btn=self.ui.button_log_export, filter_btn=self.ui.button_log_filter)
        self.ui.log_widget.layout().insertWidget(0, self.log_table)


        self.frame_layout = QGridLayout()
        self.frame_windows = QWidget(self)
        self.frame_windows.setLayout(self.frame_layout)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)

        self.frame_window_table = {}

        frame_window_node = kwargs.get("frame_window", None)
        if frame_window_node:
            self.frame_layout.setSpacing(frame_window_node.get("spacing", 8))
            num_cols = frame_window_node.get("num_cols", 3)
            num_rows = frame_window_node.get("num_rows", 2)
            size_hint = frame_window_node.get("size_hint", (512, 512))
            scale_hint = frame_window_node.get("scale_hint", 0.5)
            user_id_list = frame_window_node.get("user_id", None)
            if user_id_list:
                for i, user_id in enumerate(user_id_list):
                    fwin = FrameWindow(user_id, size_hint, scale_hint)
                    self.frame_layout.addWidget(fwin, i // num_cols, i % num_cols)
                    self.frame_window_table[str(user_id)] = fwin
            else:
                self.log_table._append_log(time_utils.now_time_log(), "critical", "MainWindow", "ui.frame_window.user_id is None")

            # receive control button
            self.button_stop_receive = QPushButton(self.ui.scrollArea)
            icon = QIcon()
            icon.addFile(u":/icons/icons/no-camera-48.png", QSize(), QIcon.Normal, QIcon.Off)
            self.button_stop_receive.setIcon(icon)
            self.button_stop_receive.setIconSize(QSize(48, 48))
            self.button_stop_receive.setCheckable(True)
            self.button_stop_receive.toggled.connect(self._on_toggle_recv)

            self.frame_button_widget = QWidget(self.ui.scrollArea)
            self.frame_button_widget.setLayout(QGridLayout())
            self.frame_button_widget.layout().setContentsMargins(0, 0, 0, 0)
            self.frame_button_widget.layout().setSpacing(5)
            self.frame_button_widget.layout().addWidget(self.button_stop_receive, 0, 0)
            self.frame_button_widget.layout().addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 1)
            self.frame_button_widget.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 0)

            i += 1
            self.frame_layout.addWidget(self.frame_button_widget, i // num_cols, i % num_cols)

        else:
            self.log_table._append_log(time_utils.now_time_log(), "critical", "MainWindow", "ui.frame_window is None")

        self.ui.scrollArea.setWidget(self.frame_windows)    

        # log receiver
        log_port = kwargs.get("log_port", "tcp://127.0.0.1:5556")
        self.log_receiver_thread = LogReceiverThread(log_port)
        self.log_receiver_thread.log_received.connect(self._update_log)
        self.log_receiver_thread.start()
        
        # image receiver
        image_port = kwargs.get("image_port", "tcp://127.0.0.1:5555")
        self.image_receiver_thread = ImageReceiverThread(image_port)
        self.image_receiver_thread.image_received.connect(self._update_image)
        self.image_receiver_thread.start()



    @Slot(str, int, QImage, int)
    def _update_image(self, device_id, frame_id, qimg, err_count):
        assert device_id in self.frame_window_table, f"device_id {device_id} not in frame_window_table"
        self.frame_window_table[device_id]._update_image(device_id, frame_id, qimg, err_count)


    @Slot(str)
    def _update_log(self, zmqmsg):
        result = log_utils.parse_log_line(zmqmsg)
        if result:
            self.log_table._append_log(*result)
        self.log_table.scrollToBottom()

    @Slot(bool)
    def _on_toggle_recv(self, checked):
        self.image_receiver_thread.set_paused(checked)

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
