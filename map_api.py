import requests
import json


class YandexMapAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://static-maps.yandex.ru/v1"

    def get_map(self, lonlat=None, spn=None, theme="light", pt=None, mode=None):
        if not mode:
            params = {
                'll': ','.join(map(str, lonlat)),
                'spn': ','.join(map(str, spn)),
                'apikey': self.api_key,
                'theme': theme
            }
            if pt:
                params['pt'] = pt
            response = requests.get(self.base_url, params=params)
            if not response:
                raise Exception(f"Ошибка запроса: {response.status_code} ({response.reason})")
            return response.content
        elif mode == 'search':
            params = {
                'spn': ','.join(map(str, spn)),
                'apikey': self.api_key,
                'theme': theme,
                'pt': pt
            }
            response = requests.get(self.base_url, params=params)
            if not response:
                raise Exception(f"Ошибка запроса: {response.status_code} ({response.reason})")
            return response.content


class GeocoderAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://geocode-maps.yandex.ru/v1/"

    def get_coordinates_and_sizes(self, address):
        params = {
            'apikey': self.api_key,
            'geocode': address,
            'format': 'json'
        }
        response = requests.get(self.base_url, params=params)
        if not response:
            raise Exception(f"Ошибка запроса: {response.status_code} ({response.reason})")

        data = json.loads(response.text)
        pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = map(float, pos.split())

        size = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']
        coords1 = size['Envelope']['lowerCorner'].split()
        coords2 = size['Envelope']['upperCorner'].split()
        sizes = [abs(float(coords1[0]) - float(coords2[0])), abs(float(coords1[1]) - float(coords2[1]))]
        return lon, lat, sizes
