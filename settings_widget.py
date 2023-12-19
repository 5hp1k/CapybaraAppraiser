from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings
from PyQt5 import uic
from capy_exceptions import InvalidSettingsException


class SettingsWidget(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('settings_widget.ui', self)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('resources/icon.png'))

        # Загрузка сохраненного состояния чекбокса
        settings = QSettings('MyApp', 'MySettings')
        saved_state = settings.value('saveBox', False, type=bool)

        print(f"Loading items from the database: {saved_state}")

        self.saveBox.setChecked(saved_state)
        self.applyButton.clicked.connect(self.apply_handler)
        self.discardButton.clicked.connect(self.discard_handler)

    def discard_handler(self):
        self.hide()
        print("Discarded settings and closed the settings window.")

    def apply_handler(self):
        # Сохранение состояния чекбокса
        settings = QSettings('MyApp', 'MySettings')
        settings.setValue('saveBox', self.saveBox.isChecked())

        if settings.value('saveBox', False, type=bool) not in [True, False]:
            raise InvalidSettingsException

        self.hide()
        print("Applied settings and closed the settings window.")
