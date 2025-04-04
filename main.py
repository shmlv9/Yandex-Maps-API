import math
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget,
                             QComboBox, QVBoxLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QCheckBox)

from apikey import API_KEY_STATIC, API_KEY_GEOCODER, API_KEY_ORGANIZATIONS
from config import MIN_SPN, MAX_SPN, MIN_LON, MAX_LON, MIN_LAT, MAX_LAT, MOVE_STEP
from map_api import YandexMapAPI, GeocoderAPI, SearchOrganizations


class MapApp(QWidget):
    def __init__(self):
        super().__init__()
        self.spn = [0.2, 0.2]
        self.lonlat = [30.3, 60]
        self.theme = "light"
        self.marker_coords = None
        self.current_address = None
        self.postal_code = True
        self.map_api = YandexMapAPI(API_KEY_STATIC)
        self.geocode_api = GeocoderAPI(API_KEY_GEOCODER)
        self.organizations_api = SearchOrganizations(API_KEY_ORGANIZATIONS)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Yandex Maps')
        self.setGeometry(100, 100, 600, 600)

        self.theme_box = QComboBox()
        self.theme_box.addItems(["Светлая", "Тёмная"])
        self.theme_box.currentTextChanged.connect(self.change_theme)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите адрес для поиска")
        self.search_input.returnPressed.connect(self.search_location)
        self.search_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.search_button = QPushButton("Искать")
        self.search_button.clicked.connect(self.search_location)

        self.remove_search_button = QPushButton("Сброс поиска")
        self.remove_search_button.clicked.connect(self.clear_marker)

        self.postcode_checkbox = QCheckBox("Показывать почтовый индекс")
        self.postcode_checkbox.setChecked(True)
        self.postcode_checkbox.stateChanged.connect(self.change_postal_code_status)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.remove_search_button)

        self.label = QLabel()
        self.label.setFixedSize(600, 450)
        self.label.mousePressEvent = self.label_mouse_press_event

        self.address_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.theme_box)
        layout.addLayout(search_layout)
        layout.addWidget(self.label)
        layout.addWidget(self.postcode_checkbox)
        layout.addWidget(self.address_label)
        self.setLayout(layout)

        self.update_map()

    def label_mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.search_input.geometry().contains(event.pos()):
                self.search_input.clearFocus()
                self.setFocus()
            self.search_location()
        elif event.button() == Qt.MouseButton.RightButton:
            x = event.pos().x()
            y = event.pos().y()

            lon, lat = self.pixel_to_geo(x, y)

            lon, lat, _, address, _ = self.geocode_api.get_info(','.join(map(str, [lon, lat])))
            self.find_organization(lon, lat, address)

    def pixel_to_geo(self, x, y):
        map_width = self.label.width()
        map_height = self.label.height()

        center_lon, center_lat = self.lonlat
        spn_lon, spn_lat = self.spn

        lon = center_lon + (x - map_width / 2) * (spn_lon / map_width)
        lat = center_lat - (y - map_height / 2) * (spn_lat / map_height)

        lon = max(MIN_LON, min(MAX_LON, lon))
        lat = max(MIN_LAT, min(MAX_LAT, lat))

        return lon, lat

    def find_organization(self, lon, lat, address):
        name, address, org_lon, org_lat = self.organizations_api.find_organization(address)
        if name and self.lonlat_distance((lon, lat), (org_lon, org_lat)) <= 50:
            self.address_label.setText(f'Ближайшая организация: {name}, {address}')
            self.marker_coords = [org_lon, org_lat]
            self.update_map()

    def lonlat_distance(self, a, b):

        degree_to_meters_factor = 111 * 1000
        a_lon, a_lat = a
        b_lon, b_lat = b

        radians_lattitude = math.radians((a_lat + b_lat) / 2.)
        lat_lon_factor = math.cos(radians_lattitude)

        dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
        dy = abs(a_lat - b_lat) * degree_to_meters_factor

        distance = math.sqrt(dx * dx + dy * dy)

        return distance

    def clear_marker(self):
        self.marker_coords = None
        self.current_address = None
        self.address_label.setText('')
        self.search_input.setText('')
        self.update_map()

    def change_postal_code_status(self):
        self.postal_code = not self.postal_code
        if self.search_input.text():
            self.search_location()

    def change_theme(self, theme):
        self.theme = 'light' if theme == 'Светлая' else 'dark'
        self.update_map()

    def search_location(self):
        search_text = self.search_input.text()
        if search_text:
            lon, lat, sizes, address, postal_code = self.geocode_api.get_info(search_text)
            self.lonlat = [lon, lat]
            self.spn = sizes
            self.marker_coords = [lon, lat]
            self.current_address = address
            if self.postal_code:
                self.address_label.setText(f"Адрес: {address}; Почтовый индекс: {postal_code}")
            else:
                self.address_label.setText(f"Адрес: {address}")
            map_data = self.map_api.get_map(
                spn=sizes,
                theme=self.theme,
                pt=f"{self.marker_coords[0]},{self.marker_coords[1]},vkbkm" if self.marker_coords else None,
                mode='search')
            self.show_map(map_data)
        else:
            lon, lat, sizes, address, postal_code = self.geocode_api.get_info(','.join(map(str, self.lonlat)))
            self.marker_coords = [lon, lat]
            self.current_address = address
            if self.postal_code:
                self.address_label.setText(f"Адрес: {address}; Почтовый индекс: {postal_code}")
            else:
                self.address_label.setText(f"Адрес: {address}")
            map_data = self.map_api.get_map(
                lonlat=self.lonlat,
                spn=self.spn,
                theme=self.theme,
                pt=f"{self.marker_coords[0]},{self.marker_coords[1]},vkbkm" if self.marker_coords else None, )
            self.show_map(map_data)

    def update_map(self):
        pt_param = f"{self.marker_coords[0]},{self.marker_coords[1]},vkbkm" if self.marker_coords else None

        map_data = self.map_api.get_map(
            lonlat=self.lonlat,
            spn=self.spn,
            theme=self.theme,
            pt=pt_param)

        self.show_map(map_data)

    def show_map(self, map_data):
        image = QImage()
        image.loadFromData(map_data)
        self.pixmap = QPixmap(image)
        self.label.setPixmap(self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.search_input.geometry().contains(event.pos()):
                self.search_input.clearFocus()
                self.setFocus()

    def keyPressEvent(self, event):
        if not self.search_input.hasFocus():
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
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec())
