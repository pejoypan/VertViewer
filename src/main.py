# main.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "assets"))

from PySide6.QtWidgets import QApplication, QStyleFactory
from widgets.mainwindow import MainWindow

import argparse
from pathlib import Path
import yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VisionEdgeRT Viewer')
    parser.add_argument('--config', type=str, help='configs for initialization', default='./init.yaml')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('windows11'))

    file_path = Path(args.config)

    config = {}
    if file_path.is_file() and file_path.exists():
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
    else:
        print(f"File '{file_path}' does not exist.")
        sys.exit(1)

    if config.get("ui", None) is None:
        print(f"ui config is None.")
        sys.exit(1)

    window = MainWindow(**config["ui"])
    window.show()
    sys.exit(app.exec())