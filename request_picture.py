import requests
from PyQt5.QtGui import QPixmap

from capy_exceptions import PictureClassInitError


class Picture:
    def __init__(self, url, title):
        if type(url) is str and type(title) is str:
            self.url = url
            self.title = title
        else:
            raise PictureClassInitError

    def render_picture(self, output_label, title_label):
        if not self.url:
            # Очистка Pixmap, если URL пуст
            output_label.clear()
            title_label.clear()
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(self.url).content)
            scaled_pixmap = pixmap.scaled(output_label.size())
            output_label.setPixmap(scaled_pixmap)

        title_label.setText(self.title)


def get_picture():
    """Получение изображения с капибарой через API с использованием библиотеки requests."""
    try:
        response = requests.get("https://api.capy.lol/v1/capybara?json=true")
        response.raise_for_status()
        data = response.json()
        url = data['data']['url']
        title = data['data']['alt']

        print(f'Successfully recieved an image: {url}\n{title}')

        # Возвращаем класс изображения
        return Picture(url, title)

    except requests.RequestException as e:
        print(f"An error occured while requesting an image: {e}")
        return Picture('', 'A error occured while requesting an image')

    except PictureClassInitError as e:
        print(e.message)