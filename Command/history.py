import sqlite3


def db_table_val(id_user: int, history: str) -> None:
    """Эта функция добавляет значения в базу данных"""
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO  test (id_user, history) VALUES (?, ?)',
                   (id_user, history))

    conn.commit()
    conn.close()




