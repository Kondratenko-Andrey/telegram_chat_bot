from typing import Dict

import requests


def _make_response(url: str, headers: Dict, params: Dict, timeout=0.5, success=200):
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=timeout
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_weather(url: str, headers: Dict, city: str, func=_make_response):
    params = {"q": city}
    response = func(url, headers=headers, params=params)

    if response.status_code != 200:
        return 'Не удалось получить ответ'

    else:
        data = response.json()
        weather_info = {
            'country': data['location']['country'],
            'current_temp': data['current']['temp_c'],
            'last_updated': data['current']["last_updated"],
            'wind': round(data['current']["wind_kph"] * 1000 / 3600, 1),
            'text': data['current']['condition']['text']
        }
        return weather_info


class SiteApiInterface():

    @staticmethod
    def get_weather():
        return _get_weather


if __name__ == '__main__':
    _make_response()
    _get_weather()
    SiteApiInterface()
