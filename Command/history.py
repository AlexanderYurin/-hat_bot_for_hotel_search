import sqlite3
from telebot import TeleBot
from typing import Optional


bot: Optional[TeleBot] = None


conn = sqlite3.connect('db/hotel_history.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(id_user: int, history: str) -> None:
    """Эта функция добавляет значения в базу данных"""

    cursor.execute('INSERT INTO  history (id_user, history) VALUES (?, ?)',
                   (id_user, history))

    conn.commit()


def search(message, user_bot: TeleBot) -> None:
    global bot
    bot = user_bot

    for i_search in cursor.execute('SELECT * FROM history'):
        if i_search[1] == message.from_user.id:
            bot.send_message(message.from_user.id, i_search[2])

    bot.send_message(message.from_user.id, 'История пуста!')
