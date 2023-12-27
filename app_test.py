import pytest
from PyQt5.QtCore import Qt
from app import MainWindow

from db_manipulate import create_table, clear_table, insert_record, Record


@pytest.fixture
def app(qtbot):
    test_app = MainWindow()
    qtbot.addWidget(test_app)
    return test_app


# Тест начального состояния, проверяющий, отжаты ли все кнопки и галочкав настройках
def test_initial_state(app):
    assert not app.check_settings()
    assert app.likeButton.isEnabled()
    assert app.dislikeButton.isEnabled()
    assert app.saveButton.isEnabled()
    assert not app.likeButton.isChecked()
    assert not app.dislikeButton.isChecked()


# Тест, кликающий на кнопку лайка
def test_toggle_like_button(app, qtbot):
    qtbot.mouseClick(app.likeButton, Qt.LeftButton)
    assert app.likeButton.isChecked()


# Тест, кликающий на кнопку дизлайка
def test_toggle_dislike_button(app, qtbot):
    qtbot.mouseClick(app.dislikeButton, Qt.LeftButton)
    assert app.dislikeButton.isChecked()


# Тест, проверяющий активна ли кнопка сохранения изображения после клика по лайку или дизлайку
def test_save_button_enabled_after_toggle(app, qtbot):
    qtbot.mouseClick(app.likeButton, Qt.LeftButton)
    assert app.saveButton.isEnabled()

    qtbot.mouseClick(app.dislikeButton, Qt.LeftButton)
    assert app.saveButton.isEnabled()


# Метод, добавялющий две записи в базу данных
@pytest.fixture
def setup_database():
    clear_table()
    create_table()
    sample_data = [
        Record(1, 'Title1', 'URL1', 'Like', 'Comment1'),
        Record(2, 'Title2', 'URL2', 'Dislike', 'Comment2'),
    ]
    for data in sample_data:
        insert_record(data)


# Тест, проверяющий, загружает ли база данных две добавленные в нее записи
def test_load_images_from_db(app, qtbot, setup_database):
    qtbot.mouseClick(app.dbButton, Qt.LeftButton)
    print("Opening db_widget...")

    app.db_widget.close()
    print("Closed db_widget...")

    assert app.db_widget.tableWidget.rowCount() == 2

    assert app.db_widget.tableWidget.item(0, 2).text() == 'URL1'
    assert app.db_widget.tableWidget.item(1, 2).text() == 'URL2'

    assert app.db_widget.tableWidget.item(0, 1).text() == 'Title1'
    assert app.db_widget.tableWidget.item(1, 1).text() == 'Title2'
