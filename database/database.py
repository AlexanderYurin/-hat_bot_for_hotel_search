import sqlite3
from datetime import datetime

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS history(
   datetime TEXT,
   search TEXT,
   id_user TEXT,
   history TEXT);
""")
conn.commit()
conn.close()


def add_user_history(user_filter, id_user, user_history):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO  history (datetime, search, id_user, history) VALUES (?, ?, ?, ?)',
                   (datetime.now(), user_filter, id_user, user_history))

    conn.commit()
    conn.close()


def history(id_user: int) -> str:
    """
    Эта функция выводит история пользователя
    :param id_user user_id
    """
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        result: list = []
        n = list(cursor.execute('SELECT * FROM history'))

        for i_search in range(len(n)):
            if n[i_search][2] == str(id_user):
                result.append(f'Время запроса: {n[i_search][0]}'
                              f'\nФильтр запроса: {n[i_search][1]}'
                              f'\n{n[i_search][3]}\n')

        if len(result) == 0:
            conn.close()
            return 'История пуста!'

        conn.close()
        return '\n'.join(result)

    except:
        return 'История пуста!'
