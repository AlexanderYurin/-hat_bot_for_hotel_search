import sqlite3

conn = sqlite3.connect('db/hotel_history.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(id_user: int, history: str) -> None:
    """Эта функция добавляет значения в базу данных"""

    cursor.execute('INSERT INTO  history (id_user, history) VALUES (?, ?)',
                   (id_user, history))

    conn.commit()


def search(id_user: int) -> str:
    for i_search in cursor.execute('SELECT * FROM history'):
        if i_search[1] == id_user:
            return i_search[2]

    else:
        return 'История пуста!'
