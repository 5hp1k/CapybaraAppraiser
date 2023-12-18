from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon
from PyQt5 import uic


class DbWidget(QDialog):  # Наследуемся от класса QDialog
    def __init__(self):
        super().__init__()
        uic.loadUi('db_widget.ui', self)
        self.setFixedSize(self.size())

        self.setWindowIcon(QIcon('resources/icon.png'))
        self.returnButton.setIcon(QIcon('resources/return.png'))

        self.returnButton.clicked.connect(self.return_handler)

    def return_handler(self):
        self.hide()


