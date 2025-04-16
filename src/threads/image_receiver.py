# receiver.py
from PySide6.QtCore import QThread, Signal
import zmq
import msgpack
import numpy as np
from PySide6.QtGui import QImage
from io import BytesIO

from utils.image_utils import cn_to_format

# TODO: is pause necessary?

class ImageReceiverThread(QThread):
    image_received = Signal(str, int, QImage, int)  # device_id, frame_id, image, err_count

    def __init__(self, zmq_address="tcp://127.0.0.1:5555", parent=None):
        super().__init__(parent)
        self.zmq_address = zmq_address
        self.paused = False
    
    def unpack_meta(self, meta_buf):
        unpacker = msgpack.Unpacker(BytesIO(meta_buf), raw=False)
        device_id = unpacker.unpack()
        frame_id = unpacker.unpack()
        h = unpacker.unpack()
        w = unpacker.unpack()
        cv_type = unpacker.unpack()
        cn = unpacker.unpack()
        timestamp = unpacker.unpack()
        err_count = unpacker.unpack()
        return device_id, frame_id, h, w, cv_type, cn, timestamp, err_count

    def set_paused(self, pause: bool):
        self.paused = pause

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.zmq_address)
        socket.setsockopt_string(zmq.SUBSCRIBE, "")  # subscribe all
        socket.setsockopt(zmq.CONFLATE, 1) # warn! only preseve the last frame
        while not self.isInterruptionRequested():
            if self.paused:
                self.msleep(100)
                continue
            try:
                if socket.poll(100):  # 100ms timeout for easy response to interrupts
                    raw = socket.recv_multipart()
                    assert len(raw) == 2, f"recv_multipart error, len(raw)={len(raw)}"
                    # if len(raw) != 2:
                    #     print("recv_multipart error")
                    #     continue

                    meta_buf = raw[0]
                    img_buf = raw[1]

                    # unpack
                    device_id, frame_id, h, w, cv_type, cn, timestamp, err_count = self.unpack_meta(meta_buf)

                    qimg = QImage(img_buf, w, h, cn_to_format(cn))

                    # emit
                    self.image_received.emit(device_id, frame_id, qimg, err_count)
            except Exception as e:
                print(f"ReceiverThread error: {e}")

        socket.close()
        context.term()
