from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QObject
from PySide6.QtGui import QPixmap

from qfluentwidgets import MessageBoxBase, SubtitleLabel, ProgressRing, IndeterminateProgressRing, IconWidget
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import assets.resources_rc

class WaitingDialog(MessageBoxBase):

    timeout = Signal()
    cancelled = Signal()
    finished = Signal() 

    def __init__(self, source: str, duration_ms: int = 0, timeout_ms: int = 5000, parent=None):
        super().__init__(parent)

        self.duration_ms = duration_ms
        self.timeout_ms = timeout_ms if timeout_ms > 0 else 5000

        self.title = SubtitleLabel(f"等待 {source}")

        self.timeout_label = IconWidget()
        self.timeout_label.setIcon(u":/icons/icons/state/exit.png")
        self.timeout_label.setFixedSize(48, 48)

        self.spinner = None
        if duration_ms > 0:
            self.spinner = ProgressRing(self)
        else:
            self.spinner = IndeterminateProgressRing(self)

        self.viewLayout.addWidget(self.title, 0, Qt.AlignTop | Qt.AlignHCenter)
        self.viewLayout.addWidget(self.spinner, 0, Qt.AlignCenter)
        self.viewLayout.addWidget(self.timeout_label, 0, Qt.AlignCenter)

        self.timeout_label.hide()
        self.yesButton.hide()

        self.cancelButton.clicked.connect(self._on_cancel)

        self._elapsed = 0
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._on_tick)
        self._progress_timer.setInterval(100)


        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)

    def show_waiting(self):
        
        if self.duration_ms > 0:
            self.spinner.setValue(0)
            self._progress_timer.start()
        elif self.timeout_ms > 0:
            self._timeout_timer.start(self.timeout_ms)

        self.show()

    @Slot()
    def stop_waiting(self):
        """external call to stop waiting"""
        if self._timeout_timer.isActive():
            self._timeout_timer.stop()
        self.finished.emit()
        self.accept()

    def _on_tick(self):
        self._elapsed += 100
        value = int((self._elapsed / self.duration_ms) * 100)
        self.spinner.setValue(min(value, 100))
        if self._elapsed >= self.duration_ms:
            self._cleanup()
            self.finished.emit()
            self.accept()

    def _on_timeout(self):
        self._cleanup()
        self.timeout.emit()
        self.spinner.hide()
        self.timeout_label.show()
        self.title.setText("等待超时")
        # self.reject()

    def _on_cancel(self):
        self._cleanup()
        self._timeout_timer.stop()
        self.cancelled.emit()
        self.reject()

    def _cleanup(self):
        self._progress_timer.stop()
        self._timeout_timer.stop()


class Waiting(QObject):
    _dialog: WaitingDialog = None

    @classmethod
    def show(cls, source: str, duration_ms: int = 0, timeout_ms: int = 5000, parent=None):
        if cls._dialog is None:
            cls._dialog = WaitingDialog(source, duration_ms, timeout_ms, parent)
            cls._dialog.finished.connect(cls._on_finished)
            cls._dialog.timeout.connect(cls._on_timeout)
            cls._dialog.cancelled.connect(cls._on_cancelled)
        cls._dialog.show_waiting()

    @classmethod
    def stop(cls):
        if cls._dialog:
            cls._dialog.stop_waiting()
            cls._dialog = None

    @classmethod
    def _on_finished(cls):
        print("[Waiter] 完成")
        cls._dialog = None

    @classmethod
    def _on_timeout(cls):
        print("[Waiter] 超时")
        cls._dialog = None

    @classmethod
    def _on_cancelled(cls):
        print("[Waiter] 用户取消")
        cls._dialog = None


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.resize(640, 480)

    window.show()

    # 测试不定时
    Waiting.show("不定时", 0, 5000, window)

    # 模拟3S后手动停止
    QTimer.singleShot(3000, lambda: Waiting.stop())

    # 测试定时
    Waiting.show("定时5s", 5000, parent=window)

    sys.exit(app.exec())