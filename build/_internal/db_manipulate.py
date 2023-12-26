import sqlite3
from sqlite3 import Error
from capy_exceptions import InvalidRecordException, RecordIdTypeException


class Record:
    """Класс записи базы данных"""
    def __init__(self, id, title, url, opinion='Neutral', comment='No comment'):
        self.id = id
        self.title = title
        self.url = url
        self.opinion = opinion
        self.comment = comment


def get_connection():
    connection = None
    try:
        connection = sqlite3.connect('capybara.db')
        return connection
    except Error as e:
        print(e)

    return connection


def create_table():
    """Создание таблицы в базе данных"""
    conn = get_connection()
    cursor = conn.cursor()

    # Создаем таблицу, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            opinion TEXT,
            comment TEXT
        )
    ''')

    conn.commit()
    conn.close()


def insert_record(record):
    """Добавление записи в базу данных"""
    conn = get_connection()
    cursor = conn.cursor()

    if type(record) is Record:
        # Вставляем данные в таблицу
        cursor.execute('''
            INSERT INTO items (id, title, url, opinion, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (record.id, record.title, record.url, record.opinion, record.comment))

        conn.commit()
        conn.close()
    else:
        raise InvalidRecordException


def update_item(record):
    conn = get_connection()
    cursor = conn.cursor()

    if type(record) is Record:
        cursor.execute("UPDATE items SET title = ?, url = ?, opinion = ?, comment = ? WHERE id = ?",
                       (record.title, record.url, record.opinion, record.comment, record.id))
        conn.commit()
        conn.close()
    else:
        raise InvalidRecordException


def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    if type(item_id) in [int, float]:
        # Удаляем запись из таблицы по id
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))

        conn.commit()
        conn.close()
    else:
        raise RecordIdTypeException


def clear_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM items')

    conn.commit()
    conn.close()


def retrieve_items():
    """Получение всех записей из базы данных"""
    conn = get_connection()
    cursor = conn.cursor()

    # Получаем все записи из таблицы
    cursor.execute('SELECT * FROM items')
    items = cursor.fetchall()

    conn.close()

    return items


def get_items_count():
    """Получение количества записей в базе данных"""
    conn = get_connection()
    cursor = conn.cursor()

    # Получаем количество записей в таблице
    cursor.execute('SELECT COUNT(*) FROM items')
    count = cursor.fetchone()[0]

    conn.close()

    return count
