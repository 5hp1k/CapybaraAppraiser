from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import db_manipulate


class DbWidget(QDialog):  # Наследуемся от класса QDialog
    def __init__(self):
        super().__init__()
        uic.loadUi('db_widget.ui', self)
        self.setFixedSize(self.size())

        db_manipulate.create_table()  # Создаем таблицу, если она не существует
        self.fill_table_widget()

        self.setWindowIcon(QIcon('resources/icon.png'))
        self.returnButton.setIcon(QIcon('resources/return.png'))

        self.returnButton.clicked.connect(self.return_handler)
        self.loadButton.clicked.connect(self.load_handler)
        self.saveButton.clicked.connect(self.save_handler)

    def return_handler(self):
        self.hide()

    def load_handler(self):
        self.fill_table_widget()

    def save_handler(self):
        for row in range(self.tableWidget.rowCount()):
            record = db_manipulate.Record(
                self.tableWidget.item(row, 0).text(),
                self.tableWidget.item(row, 1).text(),
                self.tableWidget.item(row, 2).text(),
                self.tableWidget.item(row, 3).text(),
                self.tableWidget.item(row, 4).text()
            )
            db_manipulate.update_item(record)

    def fill_table_widget(self):
        records = db_manipulate.retrieve_items()
        self.tableWidget.clear()
        num_columns = len(records[0])
        num_rows = len(records)
        self.tableWidget.setColumnCount(num_columns)
        self.tableWidget.setRowCount(num_rows)
        for i, record in enumerate(records):
            for j, field in enumerate(record):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(field)))
