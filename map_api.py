import requests


class YandexMapAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://static-maps.yandex.ru/v1"

    def get_map(self, lonlat, spn):
        params = {
            'll': ','.join(map(str, lonlat)),
            'spn': ','.join(map(str, spn)),
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        if not response:
            raise Exception(f"Ошибка запроса: {response.status_code} ({response.reason})")
        return response.content