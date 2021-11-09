import sqlite3
import time
import Data
import Other_function
import Read_file

# Проверяет тип данных в 1м столбце 2й строки в указанном листе
import SQLite


# def notifications(sheet_name):
#     some_date = Read_file.read_file(sheet_name)['Date 1']
#     meaning2 = Read_file.read_file(sheet_name)['Text 2']
#     read_type = Read_file.read_file(sheet_name)['Type']
#
#     if read_type == 'date':
#         end_text = meaning2
#         print('Бот ответил:\n' + end_text)
#     elif read_type == 'incorrect':
#         end_text = some_date
#         print('Бот ответил:\n' + end_text)
#     elif read_type == 'none':
#         end_text = some_date
#         print('Бот ответил:\n' + end_text)
#     else:
#         end_text = 'Ошибка чтения данных Notifications'
#         print('Бот ответил:\n' + end_text)
#
#     return end_text


# Функция для уведомления всех пользователей находящихся в БД
def notification_all_reg(text_message):
    try:
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        # print('Подключен к SQLite')

        sqlite_select_query = 'SELECT * from users where user_id'
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        # print('ID всех пользователей:\n')
        all_user_sql = []
        for row in records:
            all_user_sql.append(row[1])
        cursor.close()

    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print('Соединение с SQLite закрыто')

    i = 0
    while i < len(all_user_sql):
        print(all_user_sql[i])
        Data.bot.send_message(chat_id=all_user_sql[i], text=text_message)
        time.sleep(1)
        i += 1


# Уведомления для юзеров с указанными параметрами
def notification_for(text_message, column, column_meaning):
    try:
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        # print('Подключен к SQLite')

        sqlite_select_query = 'SELECT * FROM users WHERE ' + column + ' = ?'
        cursor.execute(sqlite_select_query, [column_meaning])
        records = cursor.fetchall()
        # print('Список ID:\n')
        all_id_sql = []
        for row in records:
            all_id_sql.append(row[1])
        cursor.close()
        # print(all_id_sql)
        i = 0
        print('Уведомления отправлены следующим пользователям:\n')
        while i < len(all_id_sql):
            print(all_id_sql[i])
            Data.bot.send_message(chat_id=all_id_sql[i], text=text_message)
            i += 1
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


# Уведомления для юзеров с указанными параметрами
def send_sticker_for(user_first_name, column, column_meaning):
    try:
        sticker = SQLite.get_user_sticker(Other_function.get_key(Data.user_data, user_first_name))
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        # print('Подключен к SQLite')

        sqlite_select_query = 'SELECT * FROM users WHERE ' + column + ' = ?'
        cursor.execute(sqlite_select_query, [column_meaning])
        records = cursor.fetchall()
        # print('Список ID:\n')
        all_id_sql = []
        for row in records:
            all_id_sql.append(row[1])
        cursor.close()
        # print(all_id_sql)
        i = 0
        print('Стикер отправлен следующим пользователям:\n')
        while i < len(all_id_sql):
            print(all_id_sql[i])
            Data.bot.send_sticker(all_id_sql[i], sticker)
            i += 1
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
