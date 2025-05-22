# mainwindow.py
import subprocess
import sys
import time
from pathlib import Path
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QPointF, QProcess,
    QSize, QTime, QUrl, Qt, Slot, QTimer, QStandardPaths)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QStandardItemModel, QStandardItem,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView, QStackedLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QMessageBox, QMenu, QGridLayout, QSpacerItem, QListWidgetItem,
    QTableView, QToolButton, QVBoxLayout, QWidget, QMainWindow)
from qfluentwidgets import MessageBox
from widgets.frame_window import FrameWindow
from widgets.waiting_dialog import Waiting
from threads.image_receiver import ImageReceiverThread
from threads.log_receiver import LogReceiverThread
import utils.log_utils as log_utils
import utils.time_utils as time_utils
import assets.resources_rc
from widgets.log_table import LogTable
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):

    START_DELAY = 500 # ms

    def __init__(self, **kwargs):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fixed_size = kwargs.get("size", (1920, 1080))
        self.setFixedSize(self.fixed_size[0], self.fixed_size[1])

        stretch = kwargs.get("stretch", [2, 1])
        for i, factor in enumerate(stretch):
            self.ui.main_panel.layout().setStretch(i, factor)

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
            hspacing, vspacing = frame_window_node.get("spacing", (10, 10))
            self.frame_layout.setHorizontalSpacing(hspacing)
            self.frame_layout.setVerticalSpacing(vspacing)
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

        # status list
        self.icon_error = QIcon(u":/icons/icons/state/error.png")
        self.icon_exit = QIcon(u":/icons/icons/state/exit.png")
        self.icon_waiting = QIcon(u":/icons/icons/state/waiting.png")
        self.icon_working = QIcon(u":/icons/icons/state/working.png")
        

        # start vision edge rt
        self.vert_processes = {}
        Waiting.show("启动VisionEdgeRT", timeout_ms=5000, parent=self)
        QTimer.singleShot(self.START_DELAY, self.start_vision_edge_rt)

    def start_vision_edge_rt(self):
        exe_path = Path("C:/VisionEdgeRT/bin/VERT.exe")
        if not exe_path.exists():
            w = MessageBox("Error", f"Cannot find bin @ {exe_path}.")
            w.exec()
            sys.exit(1)
        
        configs = [
                    Path("D:/repository/VertPlayground/init0.yaml"), 
                    Path("D:/repository/VertPlayground/init1.yaml"),
                    Path("D:/repository/VertPlayground/init2.yaml"),
                    Path("D:/repository/VertPlayground/init3.yaml"),
                  ]

        for i, config in enumerate(configs):
            if not config.exists():
                w = MessageBox("Error", f"Cannot find config @ {config}.")
                w.exec()
                sys.exit(1)
            
            QTimer.singleShot(i * self.START_DELAY, lambda c=config: self._start_single_proc(c, exe_path))
        

        Waiting.stop()

    def _start_single_proc(self, config, exe_path):
        short_name = config.stem
        proc = QProcess(self)
        proc.setProgram(str(exe_path))
        proc.setArguments(['--config', str(config)])
        proc.setProcessChannelMode(QProcess.MergedChannels)

        proc.started.connect(lambda cfg=short_name: self._on_vert_process_started(cfg))
        proc.finished.connect(lambda code, status, cfg=short_name: self._on_vert_process_finished(code, status, cfg))
        proc.errorOccurred.connect(lambda err, cfg=short_name: self._on_vert_process_error(cfg, err))
        proc.readyReadStandardOutput.connect(lambda cfg=short_name, p=proc: self._on_vert_process_out(cfg, p))

        proc.start()
        self.vert_processes[short_name] = proc

    @Slot(str, QIcon, str)
    def _update_process_status(self, name:str, icon:QIcon, msg:str=None):
        found = False
        for i in range(self.ui.widget_process_status.count()):
            item =self.ui.widget_process_status.item(i)
            if item.text().startswith(name):
                item.setIcon(icon)
                if msg:
                    item.setText(f"{name} - {msg}")
                found = True
                break
        if not found:
            item = QListWidgetItem()
            item.setIcon(icon)
            item.setText(f"{name} - {msg}") if msg else item.setText(name)
            self.ui.widget_process_status.addItem(item)



    @Slot(str, int, QImage, int)
    def _update_image(self, device_id, frame_id, qimg, err_count):
        assert device_id in self.frame_window_table, f"device_id {device_id} not in frame_window_table"
        self.frame_window_table[device_id]._update_image(device_id, frame_id, qimg, err_count)

    @Slot()
    def _on_vert_process_started(self, name):
        print(f"[{name}] - ⏳ 启动中...")
        log_utils.show_info_bar('success', f"⏳ 启动中...", title=name, parent=self)
        self._update_process_status(name, self.icon_waiting)

    
    @Slot()
    def _on_vert_process_finished(self, exit_code, exit_status, name):
        print(f"[{name}] - ❌ 已退出 (code: {exit_code})")
        # TODO
        # log_utils.show_info_bar('warning', f"❌ 已退出 (code: {exit_code})", title=name, parent=self)
        # self._update_process_status(name, self.icon_exit)

    @Slot()
    def _on_vert_process_error(self, name, errmsg):
        print(f"[{name}] - ❗ 错误: {errmsg}")
        # TODO
        # log_utils.show_info_bar('error', f"{errmsg}", title=name, parent=self)
        # self._update_process_status(name, self.icon_error)

    @Slot()
    def _on_vert_process_out(self, name, proc):
        line = proc.readAllStandardOutput().data().decode('utf-8').strip()
        print(f"[{name}] - ⚠️ {line}")

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
        for proc in self.vert_processes.values():
            proc.write(b'\n')
            proc.waitForBytesWritten(6000)
            proc.terminate()
            proc.waitForFinished(1000)
        print("✅ All VisionEdgeRT processes terminated.")
        self.image_receiver_thread.requestInterruption()
        self.image_receiver_thread.quit()
        self.image_receiver_thread.wait()
        self.log_receiver_thread.requestInterruption()
        self.log_receiver_thread.quit()
        self.log_receiver_thread.wait()
        print("✅ 线程退出完毕")
        event.accept()
