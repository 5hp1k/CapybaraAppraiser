from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QInputDialog, QLineEdit
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import sys

from async_picture import get_picture
from db_item import Item

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        self.setFixedSize(605, 515)

        self.setWindowIcon(QIcon('resources/icon.png'))

        icon_paths = {
            'likeButton': 'resources/like.png',
            'dislikeButton': 'resources/dislike.png',
            'saveButton': 'resources/save.png',
            'settingsButton': 'resources/settings.png'
        }

        for button_name, icon_path in icon_paths.items():
            button = self.findChild(QToolButton, button_name)
            if button:
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(32, 32))

        self.getPictureButton.clicked.connect(self.get_picture_handler)
        self.saveButton.clicked.connect(self.save_handler)

    def get_picture_handler(self):
        get_picture(self.imageLabel, self.titleLabel)
        self.getPictureButton.setText("Next Picture")

    def save_handler(self):
        text, ok_pressed = QInputDialog.getText(self, "Save",
                                                "Comment the picture you want to save:", QLineEdit.Normal, "")
        if ok_pressed and text:
            print(f"Entered text: {text}")
            save_item = Item(self.titleLabel, self.imageLabel.text, 'Like', text)

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
