# receiver.py
from PySide6.QtCore import QThread, Signal
import zmq
import msgpack
import numpy as np
from PySide6.QtGui import QImage
from io import BytesIO

class ImageReceiverThread(QThread):
    image_received = Signal(str, QImage)  # device_id, image

    def __init__(self, zmq_address="tcp://127.0.0.1:5555", parent=None):
        super().__init__(parent)
        self.zmq_address = zmq_address

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.zmq_address)
        socket.setsockopt_string(zmq.SUBSCRIBE, "")  # 订阅所有

        while not self.isInterruptionRequested():
            try:
                if socket.poll(100):  # 100ms 超时，方便响应中断
                    raw = socket.recv_multipart()
                    if len(raw) != 2:
                        print("recv_multipart error")
                        continue

                    meta_buf = raw[0]
                    img_buf = raw[1]

                    # 解包元数据
                    unpacker = msgpack.Unpacker(BytesIO(meta_buf), raw=False)
                    device_id = unpacker.unpack()
                    frame_id = unpacker.unpack()
                    h = unpacker.unpack()
                    w = unpacker.unpack()
                    cv_type = unpacker.unpack()
                    timestamp = unpacker.unpack()

                    # 构造图像
                    img = np.frombuffer(img_buf, dtype=np.uint8).reshape((h, w, 3))
                    qimg = QImage(img.data, w, h, 3 * w, QImage.Format_RGB888).rgbSwapped()

                    # 发出信号
                    self.image_received.emit(device_id, qimg)
            except Exception as e:
                print("ReceiverThread error:", e)

        socket.close()
        context.term()
