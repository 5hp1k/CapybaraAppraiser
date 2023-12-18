import requests
from PyQt5.QtGui import QPixmap


def get_picture(output_label, title_label):
    """Получение изображения с капибарой через API с использованием библиотеки requests."""
    try:
        response = requests.get("https://api.capy.lol/v1/capybara?json=true")
        response.raise_for_status()
        data = response.json()
        url = data['data']['url']
        title = data['data']['alt']

        print('Successfully recieved an image: ', url, title)

        # Загружаем изображение и отображаем его
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(url).content)
        scaled_pixmap = pixmap.scaled(output_label.size())
        output_label.setPixmap(scaled_pixmap)

        title_label.setText(title)

    except requests.RequestException as e:
        print(f"An error occured while requesting an image: {e}")
