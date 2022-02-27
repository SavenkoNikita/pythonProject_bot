import sqlite3
import time

import Data
import Other_function
import Telegram_bot


class SQL:
    """Проверка, добавление, обновление и удаление данных о пользователях"""

    def __init__(self):
        self.sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False)
        self.cursor = self.sqlite_connection.cursor()
        # if message.forward_from is not None:  # Если сообщение является пересылаемым
        #     self.user_id = message.forward_from.id
        #     self.first_name = message.forward_from.first_name
        #     self.last_name = message.forward_from.last_name
        #     self.username = message.forward_from.username
        # else:
        #     self.user_id = message.from_user.id
        #     self.first_name = message.from_user.first_name
        #     self.last_name = message.from_user.last_name
        #     self.username = message.from_user.username

    def check_for_existence(self, user_id):
        """Проверка на существование пользователя в БД"""
        info = self.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
        if info.fetchone() is None:  # Если человека нет в бд
            return False
        else:  # Если есть человек в бд
            return True

    def check_for_admin(self, user_id):
        """Проверка на то, является ли пользователь админом"""
        if self.check_for_existence(user_id) is True:
            info = self.cursor.execute('SELECT * FROM users WHERE status=? and user_id=?', ('admin', user_id))
            if info.fetchone() is None:  # Если пользователь не админ
                return False
            else:  # Если пользователь админ
                return True

    def check_for_notification(self, user_id):
        """Проверка на то, подписался ли пользователь на рассылку уведомлений"""
        if self.check_for_existence(user_id) is True:
            info = self.cursor.execute('SELECT * FROM users WHERE notification=? and user_id=?', ('yes', user_id))
            if info.fetchone() is None:  # Если пользователь НЕ подписан на рассылку
                return False
            else:  # Если пользователь подписан на рассылку
                return True

    def set_subscribe(self, user_id):
        """Присваивает статус <подписан> в БД"""
        self.update_sqlite_table('yes', user_id, 'notification')

    def set_unsubscribe(self, user_id):
        """Присваивает статус <отписан> в БД"""
        self.update_sqlite_table('no', user_id, 'notification')

    def db_table_val(self, user_id, first_name, last_name, username):
        """Проверка на уникальность и добавление данных о пользователе в SQL"""
        # Словарь вносимых в базу данных значений
        list_user = {
            'ID: ': user_id,
            'Имя: ': first_name,
            'Фамилия: ': last_name,
            'Username:  @': username
        }

        def data_user():  # Заполняем отсутствующие о пользователе данные (имя, ник и тп) фразой <нет данных>
            for a, b in list_user.items():
                if b is None:
                    b = '<нет данных>'
                    return str(a) + str(b) + '\n'
                else:
                    return str(a) + str(b) + '\n'

        if self.check_for_existence(user_id) is False:
            sqlite_select_query = 'SELECT * from users where user_id'
            self.cursor.execute(sqlite_select_query)
            records = self.cursor.fetchall()
            print('ID всех пользователей:\n')
            all_user_sql = []
            for row in records:
                all_user_sql.append(row[1])
            text_message = 'Присоединился новый пользователь. Нас уже ' + str(len(all_user_sql) + 1) + '!'
            Other_function.logging_event('info', str(text_message))

            i = 0
            while i < len(all_user_sql):
                user_name = SQL().get_user_info(all_user_sql[i])
                try:
                    print(user_name)
                    Data.bot.send_message(all_user_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Data.telebot.apihelper.ApiTelegramException:
                    text_error = 'Пользователь <' + user_name + '> заблокировал бота!'
                    print(text_error)
                    Other_function.logging_event('error', str(text_error))
                    self.log_out(all_user_sql[i])  # SQL().log_out(all_user_sql[i])
                i += 1
            self.cursor.execute('INSERT INTO users (user_id, user_first_name, user_last_name, username) VALUES (?, ?, '
                                '?, ?)',
                                (user_id, first_name, last_name, username))
            self.sqlite_connection.commit()
            self.cursor.close()
            end_text = 'К боту подключился новый пользователь!\n' + data_user() + '\n'
            Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
            print(end_text)
        elif self.check_for_existence(user_id) is True:
            # обновление изменений данных о пользователе:
            sqlite_update_query = 'UPDATE users set user_first_name = ?, user_last_name = ?, username = ? WHERE ' \
                                  'user_id =' + str(user_id)
            column_values = (first_name, last_name, username)
            self.cursor.execute(sqlite_update_query, column_values)
            self.sqlite_connection.commit()
            self.cursor.close()
            end_text = 'Обновлены данные пользователя\n' + data_user() + '\n'
            Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
            print(end_text)
        else:
            end_text = 'Пользователь уже есть в базе данных!\n' + data_user() + '\n'
            Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
            print(end_text)

        return end_text

    def update_sqlite_table(self, status, user_id, column_name):
        """Обновление статуса пользователя в SQL"""
        if self.check_for_existence(user_id) is True:
            try:
                self.cursor.execute(("Update users set " + column_name + " = ? where user_id = ?"), (status, user_id))
                self.sqlite_connection.commit()
                print("Запись успешно обновлена")
                self.cursor.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)
                Other_function.logging_event('error', str(error))
            finally:
                if self.sqlite_connection:
                    self.sqlite_connection.close()

    def log_out(self, user_id):
        """Стереть все данные о пользователе из БД"""
        try:
            if self.sqlite_connection:
                try_message = 'Все данные о пользователе <' + self.get_user_info(user_id) + '> успешно удалены из БД!'
                print(try_message)
                Other_function.logging_event('info', try_message)
                self.cursor.execute('''DELETE from users where user_id = ?''', (user_id,))
                self.sqlite_connection.commit()
                self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Other_function.logging_event('error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def update_data_user(self, message):
        """Обновить данные о пользователе"""
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        if self.check_for_existence(user_id) is True:
            try:
                self.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
                records = self.cursor.fetchall()
                for row in records:
                    user_id_SQL = row[1]
                    user_first_name_SQL = row[2]
                    user_last_name_SQL = row[3]
                    username_SQL = row[4]

                    if user_id == user_id_SQL or \
                            first_name != user_first_name_SQL or \
                            last_name != user_last_name_SQL or \
                            username != username_SQL:
                        self.db_table_val(user_id, first_name, last_name, username)
                self.cursor.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite: ", error)
                Other_function.logging_event('error', str(error))
            # finally:
            #     if self.sqlite_connection:
            #         self.sqlite_connection.close()

    def get_user_info(self, user_id):
        """Получить данные о пользователе"""
        try:
            self.cursor.execute("""select * from users where user_id = ?""", (user_id,))
            records = self.cursor.fetchall()
            for row in records:
                if row[4] is not None:  # Если в SQL есть запись о username
                    name_and_username = row[2] + ' @' + row[4]  # Получаем имя и username
                else:
                    name_and_username = row[2]  # Получаем имя
                return name_and_username
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Other_function.logging_event('error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def get_user_sticker(self, user_id):
        """Получить стикер пользователя"""
        try:
            sql_select_query = """select * from users where user_id = ?"""
            self.cursor.execute(sql_select_query, (user_id,))
            records = self.cursor.fetchall()
            for row in records:
                if row[7] is not None:  # Если в SQL есть запись о
                    return row[7]  # Получаем
                else:
                    return None  # Получаем
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Other_function.logging_event('error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def get_list_users(self):
        """Получить список всех пользователей"""
        try:
            sql_select_query = """select * from users"""
            self.cursor.execute(sql_select_query)
            records = self.cursor.fetchall()
            count_records = 'Общее количество пользователей: ' + str(len(records)) + '\n\n'
            list_data = [count_records]
            for row in records:
                user_data = 'Имя: ' + str(row[2]) + \
                            '\nФамилия: ' + str(row[3]) + \
                            '\nСтатус: ' + str(row[5]) + \
                            '\nПодписка: ' + str(row[6]) + '\n\n'
                list_data.append(user_data)
            full_list = ''.join(list_data)
            print(full_list)
            return full_list
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Other_function.logging_event('error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def set_user(self, user_id):
        """Установить пользователю права юзера"""
        self.update_sqlite_table('user', user_id, 'status')

    def set_admin(self, user_id):
        """Установить пользователю права админа"""
        self.update_sqlite_table('admin', user_id, 'status')


class Notification:
    """Методы уведомлений"""

    def __init__(self):
        self.sqlite_connection = sqlite3.connect(Data.way_sql)
        self.cursor = self.sqlite_connection.cursor()

    def all_registered(self, text_message):
        """Функция для уведомления всех пользователей находящихся в БД"""
        try:
            self.cursor.execute('SELECT * from users where user_id')
            records = self.cursor.fetchall()
            all_user_sql = []
            for row in records:
                all_user_sql.append(row[1])
            self.cursor.close()
            i = 0
            print('Уведомление отправлено следующим пользователям:\n')
            while i < len(all_user_sql):
                username = SQL().get_user_info(all_user_sql[i])
                try:
                    print(username)
                    Data.bot.send_message(all_user_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Data.telebot.apihelper.ApiTelegramException:
                    text_error = 'Пользователь <' + username + '> заблокировал бота!'
                    print(text_error)
                    Other_function.logging_event('error', str(text_error))
                    SQL().log_out(all_user_sql[i])
                i += 1
        except sqlite3.Error as error:
            print('Ошибка при работе с SQLite', error)
            Other_function.logging_event('error', error)
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print('Соединение с SQLite закрыто')

    def notification_for(self, text_message, column, column_meaning):
        """Уведомления для юзеров с указанными параметрами"""
        try:
            self.cursor.execute(('SELECT * FROM users WHERE ' + column + ' = ?'), [column_meaning])
            records = self.cursor.fetchall()
            # print('Список ID:\n')
            all_id_sql = []
            for row in records:
                all_id_sql.append(row[1])
            self.cursor.close()
            # print(all_id_sql)
            i = 0
            print('Уведомление отправлено следующим пользователям:\n')
            while i < len(all_id_sql):
                username = SQL().get_user_info(all_id_sql[i])
                try:
                    print(username)
                    Data.bot.send_message(all_id_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Data.telebot.apihelper.ApiTelegramException:
                    text_error = 'Пользователь <' + username + '> заблокировал бота!'
                    print(text_error)
                    Other_function.logging_event('error', str(text_error))
                    SQL().log_out(all_id_sql[i])
                i += 1
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Other_function.logging_event('error', error)
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def send_sticker_for(self, user_first_name, column, column_meaning):
        """Уведомления для юзеров с указанными параметрами"""
        try:
            self.cursor.execute(('SELECT * FROM users WHERE ' + column + ' = ?'), [column_meaning])
            records = self.cursor.fetchall()
            # print('Список ID:\n')
            all_id_sql = []
            for row in records:
                all_id_sql.append(row[1])
            self.cursor.close()
            # print(all_id_sql)
            i = 0
            print('Стикер отправлен следующим пользователям:\n')
            while i < len(all_id_sql):
                username = SQL().get_user_info(all_id_sql[i])
                try:
                    print(username)
                    user_sticker = SQL().get_user_sticker(Other_function.get_key(user_first_name))
                    Data.bot.send_sticker(all_id_sql[i], user_sticker)
                    # Data.bot.send_sticker(Data.list_admins.get('Никита'), user_sticker)
                except Data.telebot.apihelper.ApiTelegramException:
                    print('Пользователь <' + username + '> заблокировал бота!')
                    SQL().log_out(username)
                except Exception as e:
                    time.sleep(3)
                    Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
                    print(str(e))
                    Other_function.logging_event('error', str(e))
                i += 1
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Other_function.logging_event('error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def repeat_for_list(self, data_list, user_id, count=1):
        """Присылает {count} элементов из списка {data_list} пользователю {user_id}. Если не указать {count},
        пришлёт первый элемент из списка."""

        temporary_list = []
        for elem in range(0, count):
            Data.bot.send_message(user_id, data_list[elem])
            temporary_list.append(elem)

        print(f'{Telegram_bot.answer_bot}')
        print(temporary_list, sep='\n')
