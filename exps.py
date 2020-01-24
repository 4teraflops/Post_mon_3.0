import requests
from datetime import datetime
import sqlite3
import json
import time

# глобальные переменные
s = requests.Session()
conn = sqlite3.connect('postmon.sqlite')  # Инициируем подключение к БД
cursor = conn.cursor()
start_time = datetime.now()


def create_urls_list():
    service_cods = []
    urls = []
    stop_list_cods = []
    print(' Составляю список ссылок для итераций...')
    #  Собираем список сервис-кодов
    cursor.execute("SELECT code FROM service_cods_tst")
    for cod in cursor:
        service_cods.append(cod[0])
    #  Собираемсписок по стоп листу
    cursor.execute('SELECT code FROM stop_list')
    for stop_cod in cursor:
        stop_list_cods.append(stop_cod[0])

    for s in service_cods:  # теперь составляем список ссылок, которые будем тестить
        if s not in stop_list_cods:
            # превращаем код услуги в ссылку для теста (отсекая коды из стоп листа)
            url = (
                    'https://uat.autopays.ru/api-shop/rs/shop/test?sec-key=96abc9ad-24dc-4125-9fc4-a8072f7b83c3'
                    '&service-code=' + '{}').format(s)
            urls.append(url)  # запись в общий список ссылок
    conn.commit()
    print(" Ок")
    # если надо будет чекнуть сколько кодов услуг отсечено, выводим метрики и смотрим.
    print(f'Service cods - {len(service_cods)}')
    print(f'Stop list - {len(stop_list_cods)}')
    print(f'Urls - {len(urls)}')
    print(f'Отсечено - {(len(service_cods) - len(urls))}')

    open_urls(urls)


def open_urls(urls):
    first_id = get_cursor_id('global_answers_data') + 1  # Чтоб не было расхождений в цифрах
    for url in urls:
        r = s.get(url)
        timeout = r.elapsed.total_seconds()
        answer_text = r.text.replace('--ERROR--\ncom.techinfocom.bisys.pay.utils.shared.exception.','').replace('\n', '').replace("'", '')
        code = str(url).replace(
            'https://uat.autopays.ru/api-shop/rs/shop/test?sec-key=96abc9ad-24dc-4125-9fc4-a8072f7b83c3&service-code=',
            '')
        #  вытащил значение в виде list, забрал первое значение этого list
        category = cursor.execute(f"SELECT category FROM service_cods WHERE code = '{code}'").fetchall()[0][0]
        operation_time = datetime.now()
        cursor.execute(
            f"INSERT INTO global_answers_data VALUES (Null, '{operation_time}', '{code}', '{category}', '{timeout}', '{answer_text}', Null)")
        conn.commit()
        print(
            f'code - {code} || timeout - {timeout} || category - {category} || time - {operation_time} || answer_text - {answer_text}'
        )
    last_id = get_cursor_id('global_answers_data')
    print('Обновляю данные в часовой таблице')
    check_answers('global_answers_data', first_id, last_id)
    cursor.execute("DELETE from res_h")  # предварительно затираем то, что было в таблице res_h
    res = cursor.execute(f"SELECT * FROM global_answers_data WHERE id >= {first_id} and id <= {last_id}").fetchall()
    conn.commit()
    # Записываем результаты последней проверки в таблицу res
    for r in res:
        r1 = r[1:7:1]  # Отсек первый элемент в каждом из списков (это id, чтоб не было конфликтов)
        cursor.execute(f"INSERT INTO res_h VALUES (Null, ?, ?, ?, ?, ?, ?)", r1)
    conn.commit()


def get_cursor_id(table_name):
    line_id = cursor.execute(f"select seq from sqlite_sequence where name='{table_name}'").fetchall()[0][0]
    conn.commit()
    return line_id


def check_answers(table_name, first_id, last_id):
    # Вытащил все записи с частями ответов, котоыре значат ошибку
    word_errors = []
    cursor.execute("SELECT * FROM word_errors")
    for error in cursor:
        word_errors.append(error[1])
    id_errors = []
    for errors in word_errors:  # ищем ответы с ошибками итерацией по словарю с паттернами
        for id_error in cursor.execute(f"SELECT id FROM {table_name} WHERE answer LIKE '%{errors}%' AND id >= '{first_id}' AND id <= '{last_id}'").fetchall():
            if not id_error:  # если SELECT ничего не вернул, то перейти к следующей итерации
                continue
            else:
                id_errors.append(id_error[0])  # если нашел, то записать
    # ID записей собраны, теперь добавим им статус ошибки
    for id in id_errors:
        cursor.execute(f"UPDATE {table_name} SET status = 'Error' WHERE id = '{id}'")

    #  Теперь тоже самое с ответами, котоыре значат ОК
    word_ok = []
    cursor.execute("SELECT * FROM word_ok")
    for ok in cursor:
        word_ok.append(ok[1])
    id_oks = []
    for oks in word_ok:
        for id_ok in cursor.execute(f"SELECT id FROM {table_name} WHERE answer LIKE '%{oks}%' AND id >= '{first_id}' AND id <= '{last_id}'").fetchall():
            if not id_ok:
                continue
            else:
                id_oks.append(id_ok[0])
    for ok_res in id_oks:
        cursor.execute(f"UPDATE {table_name} SET status = 'OK' WHERE id = '{ok_res}'")
    conn.commit()
    # Теперь ошибки, связанные с форматом
    # паттерномв немного, по этому собираем данные одним запросом
    id_with_format = cursor.execute(f"SELECT id FROM global_answers_data WHERE id >= '{first_id}' AND id <= '{last_id}' AND (answer LIKE '%BIS-01275%' OR answer LIKE '%Неверный формат%' OR answer LIKE '%Недостаточно параметров%' OR answer LIKE '%Отсутствуют требуемые доп параметры%' OR answer LIKE '%BIS-01656%')").fetchall()
    for with_format in id_with_format:
        cursor.execute(f"UPDATE {table_name} SET status = 'Format' WHERE id = {with_format[0]}")

    # Теперь для невыведенных услуг
    id_shadow = cursor.execute(f"SELECT id FROM {table_name} WHERE answer LIKE 'provider == null' AND id >= '{first_id}' AND id <= '{last_id}'").fetchall()
    for shadow in id_shadow:
        cursor.execute(f"UPDATE {table_name} SET status = 'Услга не выведена' WHERE id = '{shadow[0]}'")

    conn.commit()
    # Смотрим неопознанные ошибки (которым не присвоилась категория)
    manual_check = cursor.execute(f"SELECT id FROM {table_name} WHERE status is NULL AND id >= '{first_id}' AND id <= '{last_id}'").fetchall()
    # Подсчитаем общее кол-во проанализированных ПУ
    len_all_table = cursor.execute(f"SELECT id from {table_name} WHERE id >= '{first_id}' AND id <= '{last_id}'").fetchall()
    print(len_all_table)
    # Посмотрим есть ли ошибки у клиентов категории А
    errors_a = cursor.execute(f"SELECT code, answer, status FROM {table_name} WHERE category = 'A' AND status = 'Error' AND id >= '{first_id}' AND id <= '{last_id}'").fetchall()
    # Выводим срез по цифрам:
    print(f'\nВсего проанализировано: {len(len_all_table)} ПУ.\n')
    print('Из них: \n')
    print(f'{len(id_errors)} - С техническинми ошибками')
    print(f'{len(id_oks)} - В состоянии OK')
    print(f'{len(id_with_format)} - Не совпали по формату запроса проверки')
    print(f'{len(manual_check)}   - Неопознанные ошибки')
    print(f'{len(id_shadow)} - услуга не выведена')
    print(f'\nКлиентов категории А с ошибками: {len(errors_a)}\n')
    for a in errors_a:
        print(f'Код услуги: {a[0]}\nСтатус услуги: {a[2]}\nТекст ответа: {a[1]}\n')
    conn.commit()
    if len(errors_a) > 0:
        for a in errors_a:
            alarmtext = f'Код услуги: {a[0]}\nСтатус услуги: {a[2]}\nТекст ответа: {a[1]}\n'
            do_alarm(alarmtext)


def do_alarm(alarmtext):  # отправка сообщения в канал slack
    headers = {"Content-type": "application/json"}
    url = "https://hooks.slack.com/services/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"
    payload = {"text": f"{alarmtext}"}
    requests.post(url, headers=headers, data=json.dumps(payload))


if __name__ == '__main__':
    try:
        while True:
            create_urls_list()
            end_time = datetime.now()  # для рассчета времени выполнения скрипта
            work_time = end_time - start_time  # рассчет времени вполнения скрипта
            conn.commit()
            print('\nВремя выполнения скрипта = ', work_time)
            time.sleep(15)
    except KeyboardInterrupt:
        print('\n Вы завершили работу программы. Закрываюсь.')