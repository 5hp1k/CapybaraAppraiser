from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QInputDialog, QLineEdit
from PyQt5.QtCore import QSize, QSettings
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import sys

from request_picture import get_picture
from settings_widget import SettingsWidget
from db_widget import DbWidget
from db_item import Item


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        self.setFixedSize(self.size())

        self.settings_widget = SettingsWidget()
        self.db_widget = DbWidget()

        self.setWindowIcon(QIcon('resources/icon.png'))

        icon_paths = {
            'likeButton': 'resources/like.png',
            'dislikeButton': 'resources/dislike.png',
            'saveButton': 'resources/save.png',
            'settingsButton': 'resources/settings.png',
            'dbButton': 'resources/db.png'
        }

        for button_name, icon_path in icon_paths.items():
            button = self.findChild(QToolButton, button_name)
            if button:
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(32, 32))

        self.getPictureButton.clicked.connect(self.get_picture_handler)
        self.saveButton.clicked.connect(self.save_handler)
        self.settingsButton.clicked.connect(self.open_settings)
        self.dbButton.clicked.connect(self.open_db_widget)

    def get_picture_handler(self):
        settings = QSettings('MyApp', 'MySettings')
        is_database_load = settings.value('saveBox', False, type=bool)

        if is_database_load:
            print("Loading a picture from the database...")
        else:
            print("Getting a picture via API...")
            get_picture(self.imageLabel, self.titleLabel)

        self.getPictureButton.setText("Next Picture")

    def save_handler(self):
        text, ok_pressed = QInputDialog.getText(self, "Save",
                                                "Comment the picture you want to save:", QLineEdit.Normal, "")
        if ok_pressed:
            save_item = Item(self.titleLabel, self.imageLabel.text, 'Like', text)
            print(f"Created a new item to save into the database:{save_item}")

    def open_settings(self):
        self.settings_widget.exec_()
        print('Opened settings window')

    def open_db_widget(self):
        self.db_widget.exec_()
        print('Opened database editor')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
