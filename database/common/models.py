from datetime import datetime
from peewee import SqliteDatabase, Model, DateTimeField, TextField

# Создаём базу данных на базе sqlite
db = SqliteDatabase('tg_database.db')


# Создаём базовую модель
class ModelBase(Model):
    created_at = DateTimeField(default=datetime.now().replace(microsecond=0))

    class Meta:
        database = db


# Создаем модель, которая непосредственно использоваться для хранения данных
class History(ModelBase):
    user_name = TextField()
    message = TextField()
