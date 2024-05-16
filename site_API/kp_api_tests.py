from typing import Union, Generator
from dotenv import load_dotenv
import os
import requests

session = requests.Session()
# Базовый url
url_kp = 'https://api.kinopoisk.dev'
# В заголовке указываем токен
load_dotenv()
headers_kp = {'X-API-KEY': os.getenv('KP_API_KEY'),
              "accept": "application/json"}
session.headers.update(headers_kp)
link_genres = '/v1/movie/possible-values-by-field'

# Указываем параметр для получения списка элементов данного значения
# В параметр field необходимо указать интересуемое значение(genres.name, countries.name, type, typeNumber, status)
params = {'field': "genres.name"}

# Словарь для хранения данных, предоставленных пользователем
kp_user_data = {
    'Жанр': None,
    'Рейтинг': None,
    'Количество': None,
    'Годы выхода': None

}


def data_processing(data_: dict) -> Generator:
    '''Функция для обработки полученной информации и подготовки для последующей отправки'''
    data_info = [
        {
            "Наименование фильма": el['name'],
            "Рейтинг КиноПоиск": el['rating']['kp'],
            'Год выхода': el['year'],
            'Страна': el['countries'],
            'Описание': el['description']

        }
        for el in data_["docs"]
    ]

    for ind, element in enumerate(data_info, start=1):
        send_m = ''
        send_m += f'<strong><i>\n\t*{ind}*\n</i></strong>\n'
        for param, info in element.items():
            if param == 'Страна':
                send_m += f'<strong>{param}:</strong> {", ".join([el["name"] for el in info])}\n'
            else:
                send_m += f'<strong>{param}:</strong> {info}\n'
        yield send_m


def get_genre_list() -> Union[str, tuple]:
    # Делаем запрос
    response = session.get(url_kp + link_genres, params=params)

    if response.status_code != 200:
        return "Не удалось корректно завершить поиск"

    else:

        # Формируем список жанров с указанием порядкового номера, для дальнейшего запроса у пользователя

        list_ = [(el[0], el[1]['name']) for el in enumerate(response.json(), 1)]
        str_ = '<pre>'

        str_ += f'{" " * 8}{"перечень жанров фильмов:".upper()}\n'
        for el in list_:
            str_ += f'{el[0]:>2}) {el[1].capitalize().ljust(16)} '
            if el[0] % 2 == 0:
                str_ += '\n'
        str_ += '</pre>'

    return list_, str_


try:
    list_of_genres, str_of_genres = get_genre_list()
except Exception:
    print(get_genre_list())

if __name__ == '__main__':
    get_genre_list()
