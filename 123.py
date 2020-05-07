import sqlite3

conn = sqlite3.connect('postmon.sqlite')  # Инициируем подключение к БД
cursor = conn.cursor()

f = cursor.execute("SELECT code from res_h WHERE status = 'услуга не выведена'").fetchall()


def tyu():
    for i in f:
        print(i[0])
        cursor.execute(f"INSERT INTO stop_list VALUES (Null, '{i[0]}')")
        conn.commit()


tyu()