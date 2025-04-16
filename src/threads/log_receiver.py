import zmq
from PySide6.QtCore import QThread, Signal

class LogReceiverThread(QThread):
    log_received = Signal(str)

    def __init__(self, zmq_address="tcp://127.0.0.1:5556"):
        super().__init__()
        self.zmq_address = zmq_address

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(self.zmq_address)
        while not self.isInterruptionRequested():
            try:
                msg = socket.recv_string(flags=zmq.NOBLOCK)
                self.log_received.emit(msg)
            except zmq.Again:
                QThread.msleep(100)
        
        socket.close()
        context.term()

