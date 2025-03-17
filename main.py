import os
import sys
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from apikey import API_KEY_STATIC


class MapApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Yandex Maps')
        self.setGeometry(100, 100, 600, 450)

    def show_map(self, map_file):
        self.label = QLabel(self)
        self.pixmap = QPixmap(map_file)
        self.label.setPixmap(self.pixmap)
        os.remove(map_file)

    def get_map(self, lonlat, spn):
        map_params = {
            'll': lonlat,
            'spn': spn,
            'apikey': API_KEY_STATIC
        }
        map_api_server = "https://static-maps.yandex.ru/v1"
        response = requests.get(map_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        self.show_map(map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.get_map('30,60', '5,5')
    ex.show()
    sys.exit(app.exec())