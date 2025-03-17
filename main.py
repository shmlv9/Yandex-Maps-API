import os
import sys
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from apikey import API_KEY_STATIC


class MapApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.spn = [5, 5]
        self.lonlat = [30, 60]
        self.min_spn = 0.001
        self.max_spn = 90

    def init_ui(self):
        self.setWindowTitle('Yandex Maps')
        self.setGeometry(100, 100, 600, 450)
        self.label = QLabel(self)
        self.label.resize(600, 450)

    def show_map(self, map_file):
        self.pixmap = QPixmap(map_file)
        self.label.setPixmap(self.pixmap)
        os.remove(map_file)

    def get_map(self, lonlat=None, spn=None):
        if lonlat is None:
            lonlat = self.lonlat
        if spn is None:
            spn = self.spn

        map_params = {
            'll': ','.join(map(str, lonlat)),
            'spn': ','.join(map(str, spn)),
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Plus:
            self.spn = [max(self.min_spn, self.spn[0] * 0.5), max(self.min_spn, self.spn[1] * 0.5)]
        elif event.key() == Qt.Key.Key_Minus:
            self.spn = [min(self.max_spn, self.spn[0] * 2), min(self.max_spn, self.spn[1] * 2)]
        self.get_map()

    def resizeEvent(self, event):
        self.label.resize(self.width(), self.height())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.get_map()
    ex.show()
    sys.exit(app.exec())