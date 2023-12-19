from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import db_manipulate


class DbWidget(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('db_widget.ui', self)
        self.setFixedSize(self.size())

        db_manipulate.create_table()
        self.fill_table_widget()

        self.setWindowIcon(QIcon('resources/icon.png'))
        self.returnButton.setIcon(QIcon('resources/return.png'))
        self.deleteButton.setIcon(QIcon('resources/delete.png'))

        self.returnButton.clicked.connect(self.return_handler)
        self.loadButton.clicked.connect(self.load_handler)
        self.saveButton.clicked.connect(self.save_handler)
        self.deleteButton.clicked.connect(self.delete_selected_item)

        self.tableWidget.itemSelectionChanged.connect(self.on_item_selected)

    def return_handler(self):
        self.hide()

    def load_handler(self):
        try:
            self.fill_table_widget()
        except IndexError as e:
            print('Cannot load from an empty DB', e)
            QMessageBox.critical(self, "Error", f"Cannot load from an empty DB: {e}", QMessageBox.Ok)

    def save_handler(self):
        try:
            for row in range(self.tableWidget.rowCount()):
                record = db_manipulate.Record(
                    self.tableWidget.item(row, 0).text(),
                    self.tableWidget.item(row, 1).text(),
                    self.tableWidget.item(row, 2).text(),
                    self.tableWidget.item(row, 3).text(),
                    self.tableWidget.item(row, 4).text()
                )
                db_manipulate.update_item(record)
        except AttributeError as e:
            print(f"Cannot save an empty record: {e}")
            QMessageBox.critical(self, "Error", f"Cannot save an empty record: {e}", QMessageBox.Ok)

    def fill_table_widget(self):
        try:
            records = db_manipulate.retrieve_items()
            self.tableWidget.clear()
            num_columns = len(records[0])
            num_rows = len(records)
            self.tableWidget.setColumnCount(num_columns)
            self.tableWidget.setRowCount(num_rows)
            for i, record in enumerate(records):
                for j, field in enumerate(record):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(field)))
        except IndexError as e:
            print(f'Cannot load anything from an empty database {e}')
            QMessageBox.critical(self, "Error", f'Cannot load anything '
                                                f'from an empty database {e}', QMessageBox.Ok)

    def on_item_selected(self):
        self.tableWidget.selectionModel().selectedRows()

    def delete_selected_item(self):
        selected_row = self.tableWidget.currentRow()
        try:
            if selected_row >= 0:
                # Запрашиваем подтверждение на удаление
                reply = QMessageBox.question(self, 'Delete Record', 'Are you sure you want to delete this record?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    # Получаем id записи (первая ячейка в выделенной строке)
                    item_id = int(self.tableWidget.item(selected_row, 0).text())

                    # Вызываем функцию удаления записи из базы данных
                    db_manipulate.delete_item(item_id)

                    # После удаления обновляем отображение таблицы
                    self.fill_table_widget()

                    # Добавлено явное установление количества строк
                    self.tableWidget.setRowCount(self.tableWidget.rowCount() - 1)
            else:
                QMessageBox.warning(self, 'Error', 'No record selected for deletion.', QMessageBox.Ok)
        except AttributeError as e:
            print(f"Cannot delete an empty item: {e}")
            QMessageBox.critical(self, "Error", f"Cannot delete an empty item: {e}", QMessageBox.Ok)
