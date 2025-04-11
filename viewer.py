import zmq
from msgpack import Unpacker
from io import BytesIO
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QThread, Signal, Qt
import sys

class ZMQReceiver(QThread):
    image_received = Signal(str, QImage)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5555")
        socket.setsockopt_string(zmq.SUBSCRIBE, '')

        while True:
            # raw = socket.recv()
            raw = socket.recv_multipart()
            assert len(raw) == 2, "recv_multipart error"
            print(raw[0][:20])

            unpacker = Unpacker(BytesIO(raw[0]), raw=False)
            device_id = unpacker.unpack()
            frame_id = unpacker.unpack()
            h = unpacker.unpack()
            w = unpacker.unpack()
            cv_type = unpacker.unpack()
            timestamp = unpacker.unpack()

            print(f'device_id: {device_id}, frame_id: {frame_id}, h: {h}, w: {w}, cv_type: {cv_type}, timestamp: {timestamp}')

            img_data = raw[1]

            np_type = np.uint8  # 暂仅支持 CV_8UC3
            img = np.frombuffer(img_data, dtype=np_type).reshape((h, w, 3))

            # 转 QImage
            qimg = QImage(img.data, w, h, 3 * w, QImage.Format_RGB888).rgbSwapped()
            self.image_received.emit(device_id, qimg)

class ImageWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raw Image Viewer")

        self.label = QLabel("Waiting for raw image...")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.receiver = ZMQReceiver()
        self.receiver.image_received.connect(self.update_image)
        self.receiver.start()

    def update_image(self, pipeline_id, img):
        self.setWindowTitle(f"Pipeline: {pipeline_id}")
        self.label.setPixmap(QPixmap.fromImage(img).scaled(
            640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageWindow()
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())
