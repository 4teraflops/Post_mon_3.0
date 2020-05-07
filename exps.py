import requests
from datetime import datetime
import sqlite3
import json
import time

# глобальные переменные
s = requests.Session()
# s.cert = ('src/cert.pem', 'src/dec.key')  # Подстановка сертификата
conn = sqlite3.connect('postmon.sqlite')  # Инициируем подключение к БД
cursor = conn.cursor()
start_time = datetime.now()

# Присваиваем категории, взяв данные из файла
with open('/home/sanaev-va/Рабочий стол/B', 'rU') as f:
    cods = f.read().split('\n')

cursor.execute(f'UPDATE service_cods SET category = "B" where code in {tuple(cods)}')
conn.commit()