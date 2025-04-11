# receiver.py
from PySide6.QtCore import QThread, Signal
import zmq
import msgpack
import numpy as np
from PySide6.QtGui import QImage
from io import BytesIO

from utils.image_utils import to_QImage

class ImageReceiverThread(QThread):
    image_received = Signal(str, int, QImage)  # device_id, frame_id, image

    def __init__(self, zmq_address="tcp://127.0.0.1:5555", parent=None):
        super().__init__(parent)
        self.zmq_address = zmq_address

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.zmq_address)
        socket.setsockopt_string(zmq.SUBSCRIBE, "")  # subscribe all

        while not self.isInterruptionRequested():
            try:
                if socket.poll(100):  # 100ms timeout for easy response to interrupts
                    raw = socket.recv_multipart()
                    if len(raw) != 2:
                        print("recv_multipart error")
                        continue

                    meta_buf = raw[0]
                    img_buf = raw[1]

                    # unpack
                    unpacker = msgpack.Unpacker(BytesIO(meta_buf), raw=False) # TODO: markup
                    device_id = unpacker.unpack()
                    frame_id = unpacker.unpack()
                    h = unpacker.unpack()
                    w = unpacker.unpack()
                    cv_type = unpacker.unpack()
                    timestamp = unpacker.unpack()

                    # 构造图像
                    img = np.frombuffer(img_buf, dtype=np.uint8).reshape((h, w, 3)) # TODO: by channel
                    qimg = to_QImage(img)

                    # 发出信号
                    self.image_received.emit(device_id, frame_id, qimg)
            except Exception as e:
                print("ReceiverThread error:", e)

        socket.close()
        context.term()
