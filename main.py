import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from config import MIN_SPN, MAX_SPN, MIN_LON, MAX_LON, MIN_LAT, MAX_LAT, MOVE_STEP
from map_api import YandexMapAPI
from apikey import API_KEY_STATIC


class MapApp(QWidget):
    def __init__(self):
        super().__init__()
        self.spn = [5, 5]
        self.lonlat = [30, 60]
        self.map_api = YandexMapAPI(API_KEY_STATIC)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Yandex Maps')
        self.setGeometry(100, 100, 600, 450)
        self.label = QLabel(self)
        self.label.resize(600, 450)
        self.update_map()

    def update_map(self):
        map_data = self.map_api.get_map(self.lonlat, self.spn)
        self.show_map(map_data)

    def show_map(self, map_data):
        image = QImage()
        image.loadFromData(map_data)
        self.pixmap = QPixmap(image)
        self.label.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Plus:
            self.spn = [max(MIN_SPN, self.spn[0] * 0.5), max(MIN_SPN, self.spn[1] * 0.5)]
        elif event.key() == Qt.Key.Key_Minus:
            self.spn = [min(MAX_SPN, self.spn[0] * 2), min(MAX_SPN, self.spn[1] * 2)]
        elif event.key() == Qt.Key.Key_Up:
            self.lonlat[1] = min(MAX_LAT, self.lonlat[1] + self.spn[1] * MOVE_STEP)
        elif event.key() == Qt.Key.Key_Down:
            self.lonlat[1] = max(MIN_LAT, self.lonlat[1] - self.spn[1] * MOVE_STEP)
        elif event.key() == Qt.Key.Key_Left:
            self.lonlat[0] = max(MIN_LON, self.lonlat[0] - self.spn[0] * MOVE_STEP)
        elif event.key() == Qt.Key.Key_Right:
            self.lonlat[0] = min(MAX_LON, self.lonlat[0] + self.spn[0] * MOVE_STEP)
        self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec())