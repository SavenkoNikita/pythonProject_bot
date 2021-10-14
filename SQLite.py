import sqlite3

import Data

conn = sqlite3.connect(Data.way_sql, check_same_thread=False)
cursor = conn.cursor()


# Проверка на существование пользователя в БД
def check_for_existence(user_id):
    info = cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    if info.fetchone() is None:  # Если человека нет в бд
        user_status = 'False'
        # print(user_status + ' Человека нет в бд')
    else:  # Если есть человек в бд
        user_status = 'True'
        # print(user_status + ' Человек есть в бд')
    return user_status


# Проверка на то, является ли пользователь админом
def check_for_admin(user_id):
    info = cursor.execute('SELECT * FROM users WHERE status=? and user_id=?', ('admin', user_id))
    if info.fetchone() is None:  # Если пользователь не админ
        user_status = 'False'
    else:  # Если человек админ
        user_status = 'True'
    return user_status


# Проверка на то, подписался ли пользователь на рассылку уведомлений
def check_for_notification(user_id):
    info = cursor.execute('SELECT * FROM users WHERE notification=? and user_id=?', ('yes', user_id))
    if info.fetchone() is None:  # Если пользователь НЕ подписан на рассылку
        user_status = 'False'
        # print(user_status + ' Пользователь НЕ подписан на рассылку')
    else:  # Если пользователь подписан на рассылку
        user_status = 'True'
        # print(user_status + ' Пользователь подписан на рассылку')
    return user_status


#  Проверка на уникальность и добавление данных о пользователе в SQL
def db_table_val(user_id: int, user_first_name: str, user_last_name: str, username: str):
    # Словарь вносимых в базу данных значений
    list_user = {
        'ID: ': user_id,
        'Имя: ': str(user_first_name),
        'Фамилия: ': str(user_last_name),
        'Username:  @': str(username)
    }

    def data_user():  # Заполняем отсутствующие о пользователе данные (имя, ник и тп) фразой <нет данных>
        end_data = ''
        for a, b in list_user.items():
            if b == 'None':
                b1 = '<нет данных>'
                end_data = end_data + str(a) + str(b1)
            else:
                end_data = end_data + str(a) + str(b)
            end_data = end_data + '\n'
        return end_data

    if check_for_existence(user_id) == 'False':
        # добавление пользователя:
        cursor.execute('INSERT INTO users (user_id, user_first_name, user_last_name, username) VALUES (?, ?, ?, ?)',
                       (user_id, user_first_name, user_last_name, username))
        conn.commit()
        end_text = 'К боту подключился новый пользователь!\n' + data_user() + '\n'
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
        print(end_text)
    else:
        end_text = 'Пользователь уже есть в базе данных!\n' + data_user() + '\n'
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
        print(end_text)

    return end_text


def welcome(message):
    us_id = message.from_user.id
    us_first_name = message.from_user.first_name
    us_last_name = message.from_user.last_name
    us_username = message.from_user.username

    db_table_val(user_id=us_id, user_first_name=us_first_name, user_last_name=us_last_name, username=us_username)


# # Обновление статуса пользователя в SQL
# def update_sqlite_table(status, user_id):
#     try:
#         sqlite_connection = sqlite3.connect(Data.way_sql)
#         cursor = sqlite_connection.cursor()
#         print("Подключен к SQLite")
#
#         sql_update_query = """Update users set status = ? where user_id = ?"""
#         data = (status, user_id)
#         cursor.execute(sql_update_query, data)
#         sqlite_connection.commit()
#         print("Запись успешно обновлена")
#         cursor.close()
#
#     except sqlite3.Error as error:
#         print("Ошибка при работе с SQLite", error)
#     finally:
#         if sqlite_connection:
#             sqlite_connection.close()
#             print("Соединение с SQLite закрыто")


# Обновление статуса пользователя в SQL

def update_sqlite_table(status, user_id, column_name):
    try:
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        perem = "Update users set " + column_name + " = ? where user_id = ?"

        sql_update_query = perem
        data = (status, user_id)
        cursor.execute(sql_update_query, data)
        sqlite_connection.commit()
        print("Запись успешно обновлена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def log_out(message):
    try:
        sqlite_connection = sqlite3.connect(Data.way_sql)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_delete_query = 'DELETE from users where user_id = ' + str(message.from_user.id)
        cursor.execute(sql_delete_query)
        sqlite_connection.commit()
        print("Запись успешно удалена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")



# update_sqlite_table_notification('yes', 569292074, 'notification')

# update_sqlite_table('admin', 368861606)

# check_for_existence(1827221970)
# check_for_notification(1827221970)
