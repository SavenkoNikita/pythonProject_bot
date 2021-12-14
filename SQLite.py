import sqlite3
import time

import Data


sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
# cursor = sqlite_connection.cursor()

# def connect_to_SQLite():
#     sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
#     cursor = sqlite_connection.cursor()
#     global sqlite_connection
#     global cursor


# Проверка на существование пользователя в БД
def check_for_existence(user_id):
    # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
    cursor = sqlite_connection.cursor()
    info = cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    if info.fetchone() is None:  # Если человека нет в бд
        return False
    else:  # Если есть человек в бд
        return True


# Проверка на то, является ли пользователь админом
def check_for_admin(user_id):
    # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
    cursor = sqlite_connection.cursor()
    info = cursor.execute('SELECT * FROM users WHERE status=? and user_id=?', ('admin', user_id))
    if info.fetchone() is None:  # Если пользователь не админ
        return False
    else:  # Если человек админ
        return True


# Проверка на то, подписался ли пользователь на рассылку уведомлений
def check_for_notification(user_id):
    cursor = sqlite_connection.cursor()
    info = cursor.execute('SELECT * FROM users WHERE notification=? and user_id=?', ('yes', user_id))
    if info.fetchone() is None:  # Если пользователь НЕ подписан на рассылку
        return False
    else:  # Если пользователь подписан на рассылку
        return True


#  Проверка на уникальность и добавление данных о пользователе в SQL
def db_table_val(message):
    # Словарь вносимых в базу данных значений
    list_user = {
        'ID: ': message.from_user.id,
        'Имя: ': message.from_user.first_name,
        'Фамилия: ': message.from_user.last_name,
        'Username:  @': message.from_user.username
    }

    def data_user():  # Заполняем отсутствующие о пользователе данные (имя, ник и тп) фразой <нет данных>
        for a, b in list_user.items():
            if b is None:
                b1 = '<нет данных>'
                # end_data = end_data + str(a) + str(b1)
                return str(a) + str(b1) + '\n'
            else:
                # end_data = end_data + str(a) + str(b)
                return str(a) + str(b) + '\n'
            # end_data = end_data + '\n'
        # return end_data

    if check_for_existence(message.from_user.id) is False:
        sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sqlite_select_query = 'SELECT * from users where user_id'
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print('ID всех пользователей:\n')
        all_user_sql = []
        for row in records:
            all_user_sql.append(row[1])
        text_message = 'Присоединился новый пользователь. Нас уже ' + str(len(all_user_sql) + 1) + '!'

        i = 0
        while i < len(all_user_sql):
            print(all_user_sql[i])
            Data.bot.send_message(chat_id=all_user_sql[i], text=text_message)
            time.sleep(1)
            i += 1
        cursor.execute('INSERT INTO users (user_id, user_first_name, user_last_name, username) VALUES (?, ?, ?, ?)',
                       (message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                        message.from_user.username))
        sqlite_connection.commit()
        cursor.close()
        end_text = 'К боту подключился новый пользователь!\n' + data_user() + '\n'
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
        print(end_text)
    elif check_for_existence(message.from_user.id) is True:
        # обновление изменений данных о пользователе:
        sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sqlite_update_query = 'UPDATE users set user_first_name = ?, user_last_name = ?, username = ? WHERE user_id =' \
                              + str(message.from_user.id)
        column_values = (message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        cursor.execute(sqlite_update_query, column_values)
        sqlite_connection.commit()
        cursor.close()
        end_text = 'Обновлены данные пользователя\n' + data_user() + '\n'
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
        print(end_text)
    else:
        end_text = 'Пользователь уже есть в базе данных!\n' + data_user() + '\n'
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
        print(end_text)

    return end_text


# def welcome(message):
# us_id = message.from_user.id
# us_first_name = message.from_user.first_name
# us_last_name = message.from_user.last_name
# us_username = message.from_user.username
#
# db_table_val(user_id=us_id, user_first_name=us_first_name, user_last_name=us_last_name, username=us_username)

# us_id = message.from_user.id
# us_first_name = message.from_user.first_name
# us_last_name = message.from_user.last_name
# us_username = message.from_user.username

# db_table_val(user_id=message.from_user.id, user_first_name=message.from_user.first_name,
#              user_last_name=message.from_user.last_name, username=message.from_user.username)


# Обновление статуса пользователя в SQL
def update_sqlite_table(status, user_id, column_name):
    try:
        # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sql_update_query = "Update users set " + column_name + " = ? where user_id = ?"
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
            # print("Соединение с SQLite закрыто")


def log_out(user_id):
    try:
        print('Все данные о пользователе <' + get_user_info(user_id) + '> успешно удалены из БД!')
        # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sql_delete_query = 'DELETE from users where user_id = ' + str(user_id)
        cursor.execute(sql_delete_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def update_data_user(message):
    try:
        # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sql_select_query = 'SELECT * FROM users WHERE user_id=?'
        cursor.execute(sql_select_query, (message.from_user.id,))
        records = cursor.fetchall()
        for row in records:
            user_id_SQL = row[1]
            user_first_name_SQL = row[2]
            user_last_name_SQL = row[3]
            username_SQL = row[4]

            if message.from_user.id == user_id_SQL or \
                    message.from_user.first_name != user_first_name_SQL or \
                    message.from_user.last_name != user_last_name_SQL or \
                    message.from_user.username != username_SQL:
                db_table_val(message)
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite: ", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def get_user_info(user_id):
    try:
        # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sql_select_query = """select * from users where user_id = ?"""
        cursor.execute(sql_select_query, (user_id,))
        records = cursor.fetchall()
        for row in records:
            if row[4] is not None:  # Если в SQL есть запись о username
                name_and_username = row[2] + ' @' + row[4]  # Получаем имя и username
            else:
                name_and_username = row[2]  # Получаем имя
            return name_and_username
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def get_user_sticker(user_id):
    try:
        # sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sql_select_query = """select * from users where user_id = ?"""
        cursor.execute(sql_select_query, (user_id,))
        records = cursor.fetchall()
        for row in records:
            if row[7] is not None:  # Если в SQL есть запись о
                return row[7]  # Получаем
            else:
                return None  # Получаем
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
