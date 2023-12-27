from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QInputDialog, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QSize, QSettings, QMimeData
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QCursor
from PyQt5 import uic
import sys
import urllib3

from request_picture import Picture, get_picture
from settings_widget import SettingsWidget
from db_widget import DbWidget
from db_manipulate import Record, insert_record, retrieve_items
from capy_exceptions import *


class MainWindow(QMainWindow):
    """Класс главного окна приложения"""

    def __init__(self):
        super().__init__()
        uic.loadUi('resources/ui/app.ui', self)
        self.setFixedSize(self.size())

        self.settings_widget = SettingsWidget()
        self.db_widget = DbWidget()

        self.current_image = Picture('', '')
        self.current_index = 0  # Индекс текущей картинки
        self.db_items = None

        self.setWindowIcon(QIcon('resources/images/icon.png'))

        # Путь к иконкам для кнопок
        icon_paths = {
            'likeButton': 'resources/images/like.png',
            'dislikeButton': 'resources/images/dislike.png',
            'saveButton': 'resources/images/save.png',
            'settingsButton': 'resources/images/settings.png',
            'dbButton': 'resources/images/db.png'
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

        self.imageLabel.mousePressEvent = self.mousePressEvent
        self.imageLabel.mouseMoveEvent = self.mouseMoveEvent
        self.imageLabel.mouseReleaseEvent = self.mouseReleaseEvent

        # Словарь переменных для метода drag and drop
        self.drag_data = {'start_pos': None, 'is_dragging': False}

        self.update_ui()

    def get_picture_handler(self):
        """Обработчик нажатия на кнопку getPicture"""
        try:
            if self.check_settings():  # Если в настройках стоит галочка
                print("Loading a picture from the database...")
                self.load_images_from_db()
            else:
                print("Getting a picture via API...")
                self.current_image = get_picture()
                self.current_image.render_picture(self.imageLabel, self.titleLabel)
                self.getPictureButton.setText("Next Picture")

            if self.current_image:
                self.likeButton.setChecked(False)
                self.dislikeButton.setChecked(False)

        except EmptyDataBaseException as e:
            QMessageBox.warning(self, 'Error', e.message, QMessageBox.Ok)

        except urllib3.exceptions.NameResolutionError as e:
            QMessageBox.critical(self, "Error", f'An error occurred while resolving the host name: {e}', QMessageBox.Ok)

    def save_handler(self):
        """Обработчик нажатия на кнопку сохранения изображения в БД"""
        text, ok_pressed = QInputDialog.getText(self, "Save",
                                                "Comment the picture you want to save:", QLineEdit.Normal, "")
        if ok_pressed:
            try:
                if self.current_image.url != '':
                    opinion = 'Neutral'
                    if self.likeButton.isChecked():
                        opinion = 'Like'
                    elif self.dislikeButton.isChecked():
                        opinion = 'Dislike'

                    if text == "":
                        text = " "

                    print(f'saving {self.current_image.url}')
                    save_item = Record(None, self.current_image.title, self.current_image.url,
                                       opinion, text)
                    print(f"Created a new record to save into the database:{save_item}")
                    insert_record(save_item)
                else:
                    QMessageBox.warning(self, 'Error', "Cannot save an empty image.", QMessageBox.Ok)

                self.likeButton.setChecked(False)
                self.dislikeButton.setChecked(False)

            except InvalidRecordException as e:
                QMessageBox.critical(self, "Error", f"Critical error: {e.message}", QMessageBox.Ok)

    def load_images_from_db(self):
        """Метод загрузки изображений из БД, активируемый нажатием на чекбокс в настройках"""
        self.db_items = retrieve_items()

        if self.db_items:
            urls = [item[2] for item in self.db_items]
            comments = [item[4] for item in self.db_items]

            if urls and comments:
                if '' not in urls and '' not in comments:
                    self.current_index = (self.current_index + 1) % len(self.db_items)
                    url = urls[self.current_index]
                    title = comments[self.current_index]
                    self.current_image = Picture(url, title)
                    self.getPictureButton.setText("Next Picture")
                    self.current_image.render_picture(self.imageLabel, self.titleLabel)
                else:
                    self.current_image = Picture('', 'One of the database elements has wrong URL')
                    self.current_image.render_picture(self.imageLabel, self.titleLabel)
            else:
                self.current_image = Picture('', 'No picture was loaded')
                self.current_image.render_picture(self.imageLabel, self.titleLabel)
                raise EmptyDataBaseException
        else:
            self.db_items = None
            self.current_image = Picture('', 'No picture was loaded')
            self.current_image.render_picture(self.imageLabel, self.titleLabel)
            raise EmptyDataBaseException

    def mousePressEvent(self, event):
        """Обработчик события нажатия мыши для реализации функциональности Drag and Drop"""
        if event.button() == Qt.LeftButton:
            self.drag_data['start_pos'] = event.pos()

    def mouseMoveEvent(self, event):
        """Обработчик события перемещения курсора мыши для реализации функциональности Drag and Drop"""
        if self.drag_data['start_pos'] is not None:
            mime_data = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            result = drag.exec_(Qt.MoveAction)

            global_pos = QCursor.pos()
            if not self.rect().contains(self.mapFromGlobal(global_pos)):
                self.save_image()

            drag.deleteLater()

    def mouseReleaseEvent(self, event):
        """Обработчик события отпускания левой кнопки мыши для реализации функциональности Drag and Drop"""
        self.drag_data['start_pos'] = None

    def save_image(self):
        """Сохранение изображение на ПК пользователя при перетаскивании его при помощи Drag and Drop"""
        if self.current_image.url:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                       "Images (*.png *.jpg *.bmp);;All Files (*)")
            if file_path:
                pixmap = QPixmap()
                pixmap.loadFromData(self.current_image.get_data())
                pixmap.save(file_path)
        else:
            QMessageBox.warning(self, 'Error', "Cannot download an empty image.", QMessageBox.Ok)

    def dropEvent(self, event):
        """Обработчик события drop для метода Drag and Drop"""
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            event.acceptProposedAction()
            url = mime_data.urls()[0]
            self.load_image_from_url_handler(url)

    def open_settings(self):
        """Метод открытия окна настроек"""
        self.settings_widget.exec_()
        print('Opened settings window')
        self.update_ui()

    def open_db_widget(self):
        """Метод открытия окна для взаимодействия с БД"""
        self.db_widget.exec_()
        print('Opened database editor')
        self.update_ui()

    def update_ui(self):
        """Метод, которые делает кнопки активными/неактивными в зависимости от настроек"""
        self.saveButton.setEnabled(not self.check_settings())
        self.likeButton.setEnabled(not self.check_settings())
        self.dislikeButton.setEnabled(not self.check_settings())

    @staticmethod
    def check_settings():
        """Статический метод загрузки настроек"""
        settings = QSettings('MyApp', 'MySettings')
        return settings.value('saveBox', False, type=bool)


def except_hook(cls, exception, traceback):
    """Метод, который необходим для корректного отображения ошибок PyQt5"""
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
