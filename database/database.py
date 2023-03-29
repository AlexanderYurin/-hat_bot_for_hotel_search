import sqlite3
from datetime import datetime

with sqlite3.connect('data.db') as conn:
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS history(
       datetime TEXT,
       search TEXT,
       id_user INT,
       history TEXT);
    """)
    conn.commit()


def add_user_history(user_filter: str, id_user: int, user_history: str) -> None:
    """
    Эта функция записывает данные в бд.
    :param user_filter: команда запроса от пользователя.
    :param id_user: id  пользователя.
    :param user_history: результат запроса.
    """
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()

        cursor.execute('INSERT INTO  history (datetime, search, id_user, history) VALUES (?, ?, ?, ?)',
                       (datetime.now(), user_filter, id_user, user_history))

        conn.commit()


def history(id_user: int) -> str:
    """
    Эта функция выводит историю пользователя.
    :param id_user id пользователя.
    :return: возвращает последнее 5 запросов от пользователя.
    """
    try:
        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            result: list = []
            history_user: list = list(cursor.execute(f'SELECT * FROM history WHERE id_user  = {id_user}'))
            if 5 < len(history_user):
                count_his = 6
            else:
                count_his = len(history_user)

            for i_search in range(-count_his, 0):
                result.append(f'Время запроса: {history_user[i_search][0]}'
                              f'\nФильтр запроса: {history_user[i_search][1]}'
                              f'\n{history_user[i_search][3]}\n')

            if len(result) == 0:
                return 'История пуста!'

            return '\n'.join(result)


    except Exception:
        return 'История пуста!'
