import sqlite3
import time
import Data
import Other_function
import SQLite


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
            username = SQLite.get_user_info(all_id_sql[i])
            try:
                print(username)
                Data.bot.send_message(all_id_sql[i], text=text_message)
                # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
            except Data.telebot.apihelper.ApiTelegramException:
                print('Пользователь <' + username + '> заблокировал бота!')
                SQLite.log_out(all_id_sql[i])
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
        user_sticker = SQLite.get_user_sticker(Other_function.get_key(Data.user_data, user_first_name))
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
            username = SQLite.get_user_info(all_id_sql[i])
            try:
                print(username)
                user_sticker = SQLite.get_user_sticker(Other_function.get_key(Data.user_data, user_first_name))
                Data.bot.send_sticker(all_id_sql[i], user_sticker)
                # Data.bot.send_sticker(Data.list_admins.get('Никита'), user_sticker)
            except Data.telebot.apihelper.ApiTelegramException:
                print('Пользователь <' + username + '> заблокировал бота!')
                SQLite.log_out(username)
            except Exception as e:
                time.sleep(3)
                Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
                print(str(e))
            i += 1
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
