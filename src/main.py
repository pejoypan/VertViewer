# main.py
from PySide6.QtWidgets import QMainWindow, QLabel, QApplication, QWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Slot
from threads.receiver import ImageReceiverThread
from ui.ui_frame import Ui_Frame

class FrameWindow(QWidget): # TODO: just for test now, should change to Mainwindow
    def __init__(self):
        super().__init__()
        self.ui = Ui_Frame()
        self.ui.setupUi(self)

        self.setWindowTitle("ZeroMQ Image Viewer")

        self.label = QLabel("等待图像", self)
        self.ui.scrollArea.setWidget(self.label)

        self.receiver_thread = ImageReceiverThread("tcp://127.0.0.1:5555")
        self.receiver_thread.image_received.connect(self._update_image)
        self.receiver_thread.start()

    @Slot(str, int, QImage)
    def _update_image(self, device_id, frame_id, qimg):
        pixmap = QPixmap.fromImage(qimg).scaled(self.label.size())
        self.label.setPixmap(pixmap)
        self.ui.label_user_id.setText(f'from "{device_id}"')
        self.ui.label_id.setText(f"ID: {frame_id}")

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