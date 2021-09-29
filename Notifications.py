import sqlite3
import time

import Data
import Read_file


def notifications():
    list_name = Data.sheets_file['Уведомления']
    some_date = Read_file.read_file(list_name)['Date 1']
    meaning2 = Read_file.read_file(list_name)['Text 2']
    read_type = Read_file.read_file(list_name)['Type']

    if read_type == 'date':
        end_text = meaning2
        print('Бот ответил:\n' + end_text)
    elif read_type == 'incorrect':
        end_text = some_date
        print('Бот ответил:\n' + end_text)
    elif read_type == 'none':
        end_text = some_date
        print('Бот ответил:\n' + end_text)
    else:
        end_text = 'Ошибка чтения данных Notifications'
        print('Бот ответил:\n' + end_text)

    return end_text


# notifications()

# Функция для уведомления всех пользователей находящихся в БД
def notification_all_reg(text_message):
    try:
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT * from users where user_id"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print('ID всех пользователей:\n')
        all_user_sql = []
        for row in records:
            all_user_sql.append(row[1])
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    i = 0
    while i < len(all_user_sql):
        print(all_user_sql[i])
        Data.bot.send_message(chat_id=all_user_sql[i], text=text_message)
        time.sleep(1)
        i += 1


# notification_all_reg('В тестовом режиме запущена возможность получения рассылки в личной переписке с ботом. Т.е. '
#                      'теперь необязательно присутствовать в группе Remit_IT_info, можно просто подписаться на '
#                      'уведомления. Чтобы это сделать, необходимо перейти в чат с @IT_Remit_info_bot, нажать /help и '
#                      'активировать возможность выбрав соответствующую команду.')


# Уведомление пользователей которые подписаны на обновления
def notifications_for_subscribers(text_message):
    try:
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = 'SELECT * FROM users WHERE notification = ?'
        cursor.execute(sqlite_select_query, ['yes'])
        records = cursor.fetchall()
        print('ID всех пользователей:\n')
        all_user_sql = []
        for row in records:
            all_user_sql.append(row[1])
        cursor.close()
        print(all_user_sql)
        i = 0
        while i < len(all_user_sql):
            print(all_user_sql[i])
            Data.bot.send_message(chat_id=all_user_sql[i], text=text_message)
            i += 1
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


# notifications_for_subscribers('Test')
