from typing import Union, Generator
from telebot.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import telebot

# Формирование кнопки для вызова поиска фильмов, кнопки для установки года или несольких лет выпуска фильмов
markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
button_top = KeyboardButton(text='Топ фильмов')
button_year = KeyboardButton(text='Указать интересующие годы выхода фильмов')
button_history = KeyboardButton(text='История крайних 10 запросов')
markup.add(button_top, button_year, button_history)

# Формирование кнопок с номерами жанров
markup_num_genre = InlineKeyboardMarkup(row_width=8)
num_of_genre = [InlineKeyboardButton(text=str(i), callback_data=str(i))
                for i in range(1, 33)]
markup_num_genre.add(*num_of_genre)

# Формирование кнопок лучшие/худшие фильмы
markup_rating = InlineKeyboardMarkup(row_width=2)
top = InlineKeyboardButton(text='Лучшие фильмы', callback_data='Лучшие фильмы')
low = InlineKeyboardButton(text='Худшие фильмы', callback_data='Худшие фильмы')
markup_rating.row(top, low)

# Формирование кнопок с количеством фильмов
markup_amt_films = InlineKeyboardMarkup(row_width=6)
amt_films = [InlineKeyboardButton(text=str(i * 5), callback_data=str(i * 5))
             for i in range(1, 7)]
markup_amt_films.row(*amt_films)


def check_the_year(year: str) -> Union[tuple, bool]:
    data = year.replace(' ', '').split(',')
    for el in data:
        if not el.isdigit():
            temp = el.split('-')
            if len(temp) != 2 or len(temp[0]) != len(temp[1]) != 4:
                return False
        elif len(el) != 4 or int(el) > datetime.now().year:
            return False
    return True, data


def send_films_info(bot_: telebot.TeleBot, message_: Message, iterable_object: Union[list, Generator], user_data: dict):
    bot_.send_message(message_.chat.id,
                      f'<u><strong>Топ {user_data["Количество"]} {"лучших" if user_data["Рейтинг"] == "-1" else "худших"}'
                      f' фильмов в жанре {user_data["Жанр"]}</strong></u>', parse_mode='HTML')

    for el in iterable_object:
        bot_.send_message(message_.chat.id, el, parse_mode='HTML')
