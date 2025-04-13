# main.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "assets"))

from PySide6.QtWidgets import QApplication, QStyleFactory
from widgets.mainwindow import MainWindow

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('windows11'))
    window = MainWindow("tcp://127.0.0.1:5555")
    window.show()
    sys.exit(app.exec())