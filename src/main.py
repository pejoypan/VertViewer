# main.py
from PySide6.QtWidgets import QMainWindow, QLabel, QApplication
from PySide6.QtGui import QPixmap
from threads.receiver import ImageReceiverThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroMQ Image Viewer")

        self.label = QLabel("等待图像", self)
        self.label.setFixedSize(512, 512)
        self.setCentralWidget(self.label)

        self.receiver_thread = ImageReceiverThread("tcp://127.0.0.1:5555")
        self.receiver_thread.image_received.connect(self.update_image)
        self.receiver_thread.start()

    def update_image(self, device_id, qimg):
        pixmap = QPixmap.fromImage(qimg).scaled(self.label.size())
        self.label.setPixmap(pixmap)
        self.setWindowTitle(f"图像来自设备: {device_id}")

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())