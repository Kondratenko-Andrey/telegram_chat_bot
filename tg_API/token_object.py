import telebot
from dotenv import load_dotenv
import os

# link: t.me/only_m_y_bot
load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

greetings = [r'привет', 'здравствуй', 'добрый день', 'доброе утро', "добрый вечер", "здарова", "хай", 'hello', 'hi']
farewells = ['пока', "до свидания", "всего доброго", "bye"]
