from pathlib import Path
import csv
from PySide6.QtWidgets import QTableView, QMessageBox, QToolButton
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, Slot, QStandardPaths
import utils.log_utils as log_utils
import utils.time_utils as time_utils

class LogTable(QTableView):
    def __init__(self, parent=None, clear_btn=None, export_btn=None, filter_btn:QToolButton=None):
        super().__init__(parent)

        self.model = QStandardItemModel(0, 4, self)
        self.model.setHorizontalHeaderLabels(["Time", "Level", "Source", "Detail"])
        self.setModel(self.model)

        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableView.NoEditTriggers)
        self.setColumnWidth(0, 155)   # Time
        self.setColumnWidth(1, 85)    # Level
        self.setColumnWidth(2, 60)    # Source

        self.clear_btn = clear_btn
        self.export_btn = export_btn
        self.filter_btn = filter_btn

        if self.clear_btn:
            self.clear_btn.clicked.connect(lambda: self.model.removeRows(0, self.model.rowCount()))
        
        if self.export_btn:
            self.export_btn.clicked.connect(self._export_logs)

        if self.filter_btn:
            levels = ["all", "info", "warning", "error", "critical"]
            for level in levels:
                action = self.filter_btn.addAction(level)
                action.triggered.connect(lambda checked, level=level: self._filter_logs(level))

    def _filter_logs(self, level):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 1)  # level column
            if level == "all":
                self.setRowHidden(row, False)
            else:
                self.setRowHidden(row, False if level in item.text() else True)
    
    @Slot(str)
    def _append_log(self, time_str, level_str, source, detail):
        emoji = log_utils.get_emoji(level_str)
        row = [
            QStandardItem(time_str),
            QStandardItem(f"{emoji} {level_str}"),
            QStandardItem(source),
            QStandardItem(detail),
        ]
        self.model.appendRow(row)

        # if self.model.rowCount() >= self.MAX_LOG_LINES:
        #     self.model.removeRow(self.log_model.rowCount() - 1)
        # self.model.insertRow(0, row)
    
    @Slot()
    def _export_logs(self):
        path = Path(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
        filename = f"uilogs_{time_utils.now_time()}.csv"

        save_path = (path / filename).as_posix()

        try:
            with open(save_path, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Level", "Source", "Detail"])
                for row in range(self.model.rowCount()):
                    items = [self.model.item(row, col).text() for col in range(self.model.columnCount())]
                    writer.writerow(items)
            QMessageBox.information(self, "Success", f"Log exported to\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export log:\n{e}")