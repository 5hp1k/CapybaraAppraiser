from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import QSize, QSettings
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import sys
import urllib3

from request_picture import Picture, get_picture
from settings_widget import SettingsWidget
from db_widget import DbWidget
from db_manipulate import Record, insert_item, retrieve_items


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        self.setFixedSize(self.size())

        self.settings_widget = SettingsWidget()
        self.db_widget = DbWidget()

        self.currentImage = Picture('', '')
        self.current_index = 0  # Индекс текущей картинки
        self.db_items = None

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

        self.likeButton.setCheckable(True)
        self.dislikeButton.setCheckable(True)

        self.getPictureButton.clicked.connect(self.get_picture_handler)
        self.saveButton.clicked.connect(self.save_handler)
        self.settingsButton.clicked.connect(self.open_settings)
        self.dbButton.clicked.connect(self.open_db_widget)
        self.update_ui()

    def get_picture_handler(self):
        try:
            if self.check_settings():  # Если в настройках стоит галочка
                print("Loading a picture from the database...")
                self.load_images_from_db()
            else:
                print("Getting a picture via API...")
                self.currentImage = get_picture()

            if self.currentImage:
                self.currentImage.render_picture(self.imageLabel, self.titleLabel)
                self.getPictureButton.setText("Next Picture")
                self.likeButton.setChecked(False)
                self.dislikeButton.setChecked(False)

        except urllib3.exceptions.NameResolutionError as e:
            QMessageBox.critical(self, "Error", f'An error occurred while resolving the host name: {e}', QMessageBox.Ok)

    def save_handler(self):
        text, ok_pressed = QInputDialog.getText(self, "Save",
                                                "Comment the picture you want to save:", QLineEdit.Normal, "")
        if ok_pressed:
            try:
                opinion = 'Neutral'
                if self.likeButton.isChecked():
                    opinion = 'Like'
                elif self.dislikeButton.isChecked():
                    opinion = 'Dislike'

                print(f'saving {self.currentImage.url}')
                save_item = Record(None, self.currentImage.title, self.currentImage.url,
                                   opinion, text)
                print(f"Created a new record to save into the database:{save_item}")
                insert_item(save_item)

                self.likeButton.setChecked(False)
                self.dislikeButton.setChecked(False)
            except AttributeError as e:
                QMessageBox.critical(self, "Error", f"Cannot save an empty image: {e}", QMessageBox.Ok)

    def open_settings(self):
        self.settings_widget.exec_()
        print('Opened settings window')
        self.update_ui()

    def open_db_widget(self):
        self.db_widget.exec_()
        print('Opened database editor')
        self.update_ui()

    def load_images_from_db(self):
        self.db_items = retrieve_items()

        if self.db_items:
            urls = [item[2] for item in self.db_items]
            comments = [item[4] for item in self.db_items]

            if urls and comments:
                self.current_index = (self.current_index + 1) % len(self.db_items)
                url = urls[self.current_index]
                title = comments[self.current_index]
                self.currentImage = Picture(url, title)
            else:
                print("Can't load a picture from an empty database")
                self.currentImage = Picture('', 'No picture was loaded')
        else:
            print("Can't load a picture from an empty database")
            self.db_items = None
            self.currentImage = Picture('', 'No picture was loaded')

    def update_ui(self):
        self.saveButton.setEnabled(not self.check_settings())
        self.likeButton.setEnabled(not self.check_settings())
        self.dislikeButton.setEnabled(not self.check_settings())

    @staticmethod
    def check_settings():
        settings = QSettings('MyApp', 'MySettings')
        return settings.value('saveBox', False, type=bool)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
