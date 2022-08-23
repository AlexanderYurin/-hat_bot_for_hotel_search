import sqlite3


def history(id_user: int)-> str:
    conn = sqlite3.connect('db.db')
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



