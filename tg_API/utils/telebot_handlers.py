from telebot.types import Message
from tg_API.utils.tg_func_keyboard import send_films_info, markup, markup_num_genre, markup_rating, markup_amt_films, \
    check_the_year
from tg_API.token_object import bot, greetings, farewells
from database.common.models import db, History
from site_API.core import site_api, url, headers
from database.core import crud
from site_API.kp_api_tests import session, url_kp, list_of_genres, str_of_genres, kp_user_data, data_processing

db_write = crud.create()
db_read = crud.retrieve()
weather = site_api.get_weather()


@bot.message_handler(commands=['start'])
def start_(message: Message) -> None:
    kp_user_data[message.chat.id] = {}
    kp_user_data[message.chat.id]['user_name'] = f'{message.from_user.first_name} {message.from_user.last_name}'
    with open(r'tg_API\utils\start.gif', 'rb') as file:
        bot.send_animation(message.chat.id, file)

    bot.send_message(message.chat.id,
                     f'<strong><i>\nТестовый вариант чат-бота от Кондратенко Андрея!\n</i></strong>'
                     f'Для составления перечня фильмов нажмите на кнопку: \n<u>Топ фильмов</u>\n'
                     f'При необходимости указания определённого года или периода выпуска фильмов нажмите '
                     f'на кнопку: \n<u>Указать интересующие годы выхода фильмов</u>\n'
                     f'Для получения инфо по погоде введите в чат:   \n<u>погода "<i>город</i></u>"\n\n'
                     f'<i> бот отвечает на приветствие и прощание\n сообщения, которые не относятся'
                     f' к категориям записываются в базу данных</i>', parse_mode='HTML', reply_markup=markup)


@bot.message_handler(func=lambda x: any(el in x.text.lower() for el in greetings))
def bot_greeting(message: Message) -> None:
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
    with open(r'tg_API\utils\hello.gif', 'rb') as file:
        bot.send_animation(message.chat.id, file)
    data = {'user_name': f'{message.from_user.first_name} {message.from_user.last_name}', 'message': message.text}
    db_write(db, History, data)


@bot.message_handler(func=lambda x: any(el in x.text.lower() for el in farewells))
def bot_farewell(message: Message) -> None:
    bot.send_message(message.chat.id, 'Всего доброго!')
    with open(r'tg_API\utils\bye.gif', 'rb') as file:
        bot.send_animation(message.chat.id, file)
    data = {'user_name': f'{message.from_user.first_name} {message.from_user.last_name}', 'message': message.text}
    db_write(db, History, data)


@bot.message_handler(func=lambda x: 'погода' in x.text.lower())
def get_weather(message: Message) -> None:
    city = message.text.split()[-1]

    if not city.isalpha():
        bot.send_message(message.chat.id, 'Некорреткно введено наименование города!')
        return

    weather_data = weather(url, headers, city=city)
    data = {'user_name': f'{message.from_user.first_name} {message.from_user.last_name}', 'message': message.text}
    db_write(db, History, data)
    bot.send_message(message.chat.id,
                     f'<u><strong>Погода в городе {city.capitalize()}:</strong></u>', parse_mode='HTML')

    for k, v in weather_data.items():
        bot.send_message(message.chat.id, f'{k}: {v}')


# Ловим команду базовой кнопки 'топ фильмов' (кнопка KeyboardButton)
@bot.message_handler(func=lambda x: 'топ фильмов' in x.text.lower())
def kp_api_test(message: Message):
    if message.chat.id not in kp_user_data:
        kp_user_data[message.chat.id] = {}

    kp_user_data[message.chat.id]['user_name'] = f'{message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, str_of_genres, parse_mode='HTML')
    # Запрашиваем индекс интересующего жанра
    bot.send_message(message.chat.id,
                     '\nВыберете номер интересующего жанра фильма согласно перечня выше: ',
                     reply_markup=markup_num_genre)


# Ловим команду базовой кнопки 'Указать интересующие годы выхода фильмов' (кнопка KeyboardButton)
@bot.message_handler(func=lambda x: 'указать интересующие годы выхода фильмов' in x.text.lower())
def film_years(message):
    if message.chat.id not in kp_user_data:
        kp_user_data[message.chat.id] = {}
    mesg = bot.send_message(message.chat.id, '\nВведите интересующий год фильма или годы через запятую. '
                                             'Также можно указать период идущих подряд лет через дефис.')
    bot.register_next_step_handler(mesg, set_year)


def set_year(message):
    '''Функция получения интересующих лет выхода фильмов'''

    if not check_the_year(message.text):
        bot.send_message(message.chat.id, 'Данные введены некорректно!\n'
                                          'При необходимости ввести интересующие годы выхода '
                                          'фильмов нажмите необходимую кнопку ещё раз.')
        return

    kp_user_data[message.chat.id]['Годы выхода'] = check_the_year(message.text)[1]
    bot.send_message(message.chat.id,
                     'Для составления перечня фильмов нажмите на кнопку: Топ фильмов. '
                     'После составления перечня фильмов информация по интересующему году выпуска будет удалена.')


# Ловим команду базовой кнопки 'История крайних 10 запросов' (кнопка KeyboardButton)
@bot.message_handler(func=lambda x: 'история крайних 10 запросов' in x.text.lower())
def chat_history(message):
    # Формируем выборку с базы History строк, в которых в столбце message присутствует слово "Поиск"
    # для отбора запросов по фильмам
    query = db_read(db, History).where(History.message.contains('Поиск'))
    # Создаём список для сохранения необходимых строк, в необходимом формате для вывода
    data = list()
    # Отбираем последние 10 строк из перечня отсортированного по датам в убывающем порядке и заносим в список
    for row in query.order_by(History.created_at.desc()).limit(10):
        data.insert(0, f'{row.created_at}\n{row.user_name}: {row.message}')
    # Направляем пользователю строки
    for row in data:
        bot.send_message(message.chat.id, row)


# Обработчик отклика кнопок, критерий по которому ловим - кол-во кнопок первой строки клавиатуры,
# использую метод callback.message.reply_markup.keyboard[0], т.о. определяем какая клавиатура даёт отклик и для каждой
# применяем свои операции
@bot.callback_query_handler(func=lambda callback: callback.data)
def button_callback(callback):
    if len(callback.message.reply_markup.keyboard[0]) == 8:
        kp_user_data[callback.message.chat.id]['Жанр'] = list_of_genres[int(callback.data) - 1][1]
        bot.send_message(callback.message.chat.id, f'Вы выбрали жанр {kp_user_data[callback.message.chat.id]["Жанр"]}')
        # Запрашиваем высокий рейтинг или низкий рейтинг
        bot.send_message(callback.message.chat.id,
                         '\nВас интересуют лучшие фильмы данного жанра с высоким '
                         'рейтингом Кинопоиск или худшие с низким рейтингом?',
                         reply_markup=markup_rating)

    elif len(callback.message.reply_markup.keyboard[0]) == 2:
        kp_user_data[callback.message.chat.id]['Рейтинг'] = '-1' if callback.data == "Лучшие фильмы" else "1"
        bot.send_message(callback.message.chat.id,
                         'Выберете кол-во фильмов из которых будет состоять список:',
                         reply_markup=markup_amt_films)

    elif len(callback.message.reply_markup.keyboard[0]) == 6:
        kp_user_data[callback.message.chat.id]['Количество'] = int(callback.data)
        film_chart(callback.message)


# Функция вывода итоговой информации
def film_chart(message):
    db_str = (
        f'Поиск {kp_user_data[message.chat.id]["Количество"]} {"лучших" if kp_user_data[message.chat.id]["Рейтинг"] == "-1" else "худших"} '
        f'фильмов жанра {kp_user_data[message.chat.id]["Жанр"]}')

    data = {'user_name': kp_user_data[message.chat.id]['user_name'], 'message': db_str}
    db_write(db, History, data)

    params = {'page': 1,
              'limit': kp_user_data[message.chat.id]['Количество'],
              'selectFields': ['name', 'description', 'year', 'rating', 'countries'],
              'genres.name': kp_user_data[message.chat.id]['Жанр'],
              'type': ['movie', 'cartoon', 'anime'],
              'sortField': 'rating.kp',
              'rating.kp': '1-10',
              'sortType': kp_user_data[message.chat.id]['Рейтинг']}

    if 'Годы выхода' in kp_user_data[message.chat.id] and kp_user_data[message.chat.id]['Годы выхода']:
        params['year'] = kp_user_data[message.chat.id]['Годы выхода']

    data = session.get(url_kp + '/v1.4/movie', params=params)
    if data.status_code != 200:
        return "Не удалось корректно завершить поиск"
    else:
        send_films_info(bot_=bot, message_=message, iterable_object=data_processing(data.json()),
                        user_data=kp_user_data)

    kp_user_data[message.chat.id]['Годы выхода'] = None

    if message.chat.id in kp_user_data:
        del kp_user_data[message.chat.id]


@bot.message_handler(func=lambda x: True)
def default(message: Message):
    bot.reply_to(message, 'Что ты имеешь в виду?')
    with open(r'tg_API\utils\spy.gif', 'rb') as file:
        bot.send_animation(message.chat.id, file)
    data = {'user_name': f'{message.from_user.first_name} {message.from_user.last_name}', 'message': message.text}
    db_write(db, History, data)
