import datetime
import logging
import random
import sqlite3
import time

import Data
from Data import list_command_admin, list_command_user
from datetime import datetime, date, timedelta


def get_key(user_name):
    """Проверяет среди словаря есть ли в нём имя{user_name} и возвращает соответствующий id_telegram"""

    # key = 'Имя не найдено или человек не относится к дежурным. Error Other_function.get_key.'
    for keys, v in Data.user_data.items():
        for a in v:
            if a == user_name:
                key = keys
                return key


def get_data_user_SQL(user_name):
    """Принимает на вход Имя, проверяет есть ли это имя в списке дежурных, если есть, получает user_id, если он есть в
    БД, подтягивает Имя и user_name. Результат - <имя + @username>"""

    id_telegram = get_key(user_name)  # Присваиваем id из get_key
    print(id_telegram)
    if id_telegram is not None:  # Если id есть то
        if SQL().check_for_existence(id_telegram) is True:  # Если в SQL есть такой id
            end_text = SQL().get_user_info(id_telegram)  # Получаем склейку <имя + @username>
            print(end_text)
            return end_text


def logging_event(way_log, condition, text):
    """Возможные варианты записи логов - 'debug', 'info', 'warning', 'error', 'critical'"""

    if text is not None:
        logging.basicConfig(filename=way_log, level=logging.INFO,
                            format="%(asctime)s - [%(levelname)s] - %(message)s")
        if condition == 'debug':
            logging.debug(f'{text}\n\n')
        elif condition == 'info':
            logging.info(f'{text}\n\n')
        elif condition == 'warning':
            logging.warning(f'{text}\n\n')
        elif condition == 'error':
            logging.error(f'{text}\n\n')
        elif condition == 'critical':
            logging.critical(f'{text}\n\n')


def logging_sensors(condition, text_log):
    """Записывает логи показаний датчиков. На вход принимает записываемый в файл текст. Возможные варианты записи
    логов - 'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Data.way_to_log_sensors, condition, text_log)


def logging_scheduler(condition, text_log):
    """Записывает логи schedule. На вход принимает записываемый в файл текст. Возможные варианты записи логов -
    'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Data.way_to_log_scheduler, condition, text_log)


def logging_telegram_bot(condition, text_log):
    """Записывает логи работы бота. На вход принимает записываемый в файл текст. Возможные варианты записи логов -
    'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Data.way_to_log_telegram_bot, condition, text_log)


def logging_file_processing(condition, text_log):
    """Записывает логи работы с файлом. На вход принимает записываемый в файл текст. Возможные варианты записи логов -
    'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Data.way_to_log_file_processing, condition, text_log)


def can_do_it(x):
    """Перечисляет строка за строкой всё что есть в списке с переводом строки."""

    cd = ('\n'.join(map(str, x)))
    return cd


def can_help(user_id):
    """Формирует список доступных команд для пользователя в зависимости админ он или нет."""

    end_text = f'Вот что я умею:\n'
    check_admin = SQL().check_for_admin(user_id)
    if check_admin is True:  # Если пользователь админ
        end_text = end_text + can_do_it(list_command_admin)  # Передать полный список доступных команд
    else:  # Если пользователь НЕ админ
        end_text = end_text + can_do_it(list_command_user)  # Передать список команд доступных юзеру
    return end_text


def random_name():
    """Присылает уведомление кто сегодня закрывает сигналы"""
    if datetime.today().isoweekday() <= 5:
        list_name = ['Паша', 'Дима', 'Никита']
        rand_name = random.choice(list_name)
        end_text = f'Случайным образом определено, что в цеху сегодня работает {rand_name}'
        for i in list_name:
            Data.bot.send_message(chat_id=Data.list_admins.get(i), text=end_text)


class SQL:
    """Проверка, добавление, обновление и удаление данных о пользователях"""

    def __init__(self):
        self.sqlite_connection = sqlite3.connect(Data.way_sql, check_same_thread=False, timeout=10)
        self.cursor = self.sqlite_connection.cursor()

    def check_verify_in_ERP(self, user_id):
        """Проверка на то, прошёл ли пользователь верификацию в 1С. Возвращает True или False"""

        try:
            if self.check_for_existence(user_id) is True:
                status_ERP = self.cursor.execute(f'SELECT * FROM users WHERE verify_erp="yes" and user_id={user_id}')
                if status_ERP.fetchone() is None:  # Если пользователь не верифицирован в 1С
                    return False
                else:  # Если пользователь верифицирован в 1С
                    return True
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def check_for_existence(self, user_id, table_DB='users'):
        """Проверка на существование пользователя в БД"""

        try:
            # info = self.cursor.execute(f'SELECT * FROM {table_DB} WHERE user_id=?', (user_id,))
            info = self.cursor.execute(f'SELECT * FROM {table_DB} WHERE user_id="{user_id}"')
            if info.fetchone() is None:  # Если человека нет в бд
                return False
            else:  # Если есть человек в бд
                return True
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def check_for_admin(self, user_id):
        """Проверка на то, является ли пользователь админом"""
        if self.check_for_existence(user_id) is True:
            # info = self.cursor.execute('SELECT * FROM users WHERE status=? and user_id=?', ('admin', user_id))
            info = self.cursor.execute(f'SELECT * FROM users WHERE status="admin" and user_id="{user_id}"')
            if info.fetchone() is None:  # Если пользователь не админ
                return False
            else:  # Если пользователь админ
                return True

    def change_status_DB(self, user_id, column_bd):
        """Меняет у {user_id} в БД статус {column_bd} c 'yes' на 'no' и наоборот в зависимости от текущего статуса."""

        status = self.check_status_DB(user_id, column_bd, 'yes')

        if status is False:
            self.update_sqlite_table('yes', user_id, column_bd)
        else:
            self.update_sqlite_table('no', user_id, column_bd)

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
            logging_event(Data.way_to_log_telegram_bot, 'info', str(text_message))

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
                    logging_event(Data.way_to_log_telegram_bot, 'error', str(text_error))
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
            sqlite_update_query = f'UPDATE users set user_first_name = ?, user_last_name = ?, username = ? ' \
                                  f'WHERE user_id = {user_id}'
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
                self.cursor.execute(f"Update users set {column_name} = ? where user_id = ?", (status, user_id))
                # self.cursor.execute(f"Update users set {column_name} = {status} where user_id = {user_id}")
                self.sqlite_connection.commit()
                print("Запись успешно обновлена")
                self.cursor.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)
                logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
            finally:
                if self.sqlite_connection:
                    self.sqlite_connection.close()

    def log_out(self, user_id, table_name_DB='users'):
        """Стереть все данные о пользователе из БД"""
        try:
            if self.sqlite_connection:
                try_message = f'Все данные о пользователе <{self.get_user_info(user_id)}> успешно удалены ' \
                              f'из {table_name_DB}! '
                print(try_message)
                logging_event(Data.way_to_log_telegram_bot, 'info', try_message)
                self.cursor.execute(f'DELETE from {table_name_DB} where user_id = ?', (user_id,))
                self.sqlite_connection.commit()
                self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def update_data_user(self, message):
        """Обновить данные о пользователе"""
        user_id = message.from_user.id
        # user_id = message.id и далее везде
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
                logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
            # finally:
            #     if self.sqlite_connection:
            #         self.sqlite_connection.close()

    def get_user_info(self, user_id, table_name='users', column_name='user_id'):
        """Получить данные о пользователе"""
        try:
            self.cursor.execute(f"select * from {table_name} where {column_name} = ?", (user_id,))
            records = self.cursor.fetchall()
            for row in records:
                if row[4] is not None:  # Если в SQL есть запись о username
                    name_and_username = f'{row[2]} @{row[4]}'  # Получаем имя и username
                else:
                    name_and_username = row[2]  # Получаем имя
                return name_and_username
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def get_a_user_sticker_from_the_database(self, user_id):
        """Получить стикер пользователя"""
        try:
            request = f'''SELECT sticker FROM users WHERE user_id = "{user_id}"'''
            self.cursor.execute(request)
            sticker = self.cursor.fetchone()[0]
            if sticker is not None:
                return sticker
            else:
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

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
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def set_user(self, user_id):
        """Установить пользователю права юзера"""
        self.update_sqlite_table('user', user_id, 'status')

    def set_admin(self, user_id):
        """Установить пользователю права админа"""
        self.update_sqlite_table('admin', user_id, 'status')

    def check_status_DB(self, user_id, column_name, status, table_DB='users'):
        f"""Проверяет у конкретного {user_id} соответствует ли {status} в колонке {column_name}."""

        try:
            request = f'select * from {table_DB} where user_id = ? and {column_name} = ?'
            self.cursor.execute(request, (user_id, status))
            user = self.cursor.fetchone()
            if user is not None:
                return True
            else:
                return False
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def create_list_users(self, column_name_DB, column_meaning, name_table_DB='users'):
        """Формирует список пользователей с подходящими параметрами. Например, список id_user которые подписаны на
        уведомления. На вход принимает имя колонки из БД и значение ячейки. Результат list[user_id]."""

        try:
            info = self.cursor.execute(f'SELECT * FROM {name_table_DB} WHERE {column_name_DB}=?', (column_meaning,))
            records = self.cursor.fetchall()

            list_users_id = []

            for row in records:
                if info.fetchone() is None:  # Если есть совпадение по запросу
                    list_users_id.append(row[1])

            if len(list_users_id) == 0:
                return None
            else:
                return list_users_id
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def get_mess_id(self, user_id):
        """Проверяет есть ли message_id в tracking_sensor_defroster и если есть возвращает его"""

        try:
            request = f'select * from tracking_sensor_defroster where user_id = ?'
            self.cursor.execute(request, (user_id,))
            row = self.cursor.fetchone()
            if row is not None:
                return row[1]
            else:
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def add_user_by_table(self, user_id, column_name, status, name_table_DB):
        f"""Если пользователь подписан на {column_name} и отсутствует в {name_table_DB}, добавляет его."""

        try:
            if self.check_status_DB(user_id, column_name, status) is True:
                if self.check_for_existence(user_id, name_table_DB) is False:
                    self.cursor.execute(f'INSERT INTO {name_table_DB} (user_id, message_id) VALUES (?, ?)',
                                        (user_id, None))
                    self.sqlite_connection.commit()
                    self.cursor.close()
                    print(f'Пользователь {user_id} успешно добавлен в таблицу {name_table_DB}')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def update_mess_id_by_table(self, user_id, message_id, table_name_DB, name_column_in_table_users):
        f"""В таблице {table_name_DB} обновляет пользователю {user_id} значение {message_id}"""

        try:
            if self.check_status_DB(user_id, name_column_in_table_users, 'yes') is True:
                if self.check_for_existence(user_id, table_name_DB) is True:
                    # обновление изменений данных о сообщении:
                    sqlite_update_query = f'UPDATE {table_name_DB} set message_id={message_id} ' \
                                          f'WHERE user_id={user_id}'
                    self.cursor.execute(sqlite_update_query)
                    self.sqlite_connection.commit()
                    self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def get_dict(self, table_name_DB):
        """Получить список user_id и message_id"""

        try:
            request = f'select * from {table_name_DB}'
            self.cursor.execute(request)
            row = self.cursor.fetchall()
            return row
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def talk(self, text_message):
        """Ищет в БД ответ на вопрос. Принимает текст сообщения. Если есть ответ, возвращает его,
        а если нет, возвращает None"""

        try:
            request = f'select * from talk where question = ?'
            self.cursor.execute(request, (text_message,))
            row = self.cursor.fetchone()
            if row is not None:
                return row[1]
            else:
                self.insert_data_speak_DB(text_message)
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def insert_data_speak_DB(self, text_message):
        """Если вопрос отсутствует в БД, добавляет его."""

        try:
            self.cursor.execute(f'INSERT INTO talk (question, answer) VALUES (?, ?)',
                                (text_message, None))
            self.sqlite_connection.commit()
            self.cursor.close()
            print(f'Запись {text_message} успешно добавлена в таблицу talk')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def update_answer_speak_DB(self, question, answer):
        """"""

        try:
            sqlite_update_query = f'UPDATE talk set answer=? WHERE question=?'
            self.cursor.execute(sqlite_update_query, (answer, question,))
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def count_not_answer(self, count=0):
        """Считает кол-во вопросов без ответа. Результат - число."""

        try:
            self.cursor.execute('select * from talk')
            row = self.cursor.fetchall()
            for rows in row:
                # print(rows[1])
                if rows[1] is None:
                    count += 1

            # count_none_rows = f'На данный момент есть {count} вопросов без ответа.'
            return count
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def search_not_answer(self):
        """Находит первый вопрос без ответа. Результат - текст вопроса."""

        try:
            self.cursor.execute('select * from talk')
            row = self.cursor.fetchall()
            for rows in row:
                if rows[0] is not None:
                    if rows[1] is None:
                        text = rows[0]
                        return text

            text = 'Нет вопросов без ответа :)'
            return text

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def update_data_in_table_SQL(self, name_table, set_name_column, set_value_column):

        """Обновляет данные в таблице {name_table},
        устанавливает в колонке {set_name_column} значение {set_value_column}"""

        try:
            sqlite_update_query = f'UPDATE {name_table} set {set_name_column}=?'  # WHERE {where_name_column}=?'
            self.cursor.execute(sqlite_update_query, (set_value_column,))  # , where_value_column,))
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def select_data(self, name_table):
        """"""

        try:
            self.cursor.execute(f'SELECT * FROM {name_table}')
            records = self.cursor.fetchall()
            self.cursor.close()
            return records
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite: ", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    #  Работа с тестированием сотрудников
    def insert_data(self, user_id, number_test, id_question):
        """Заполняет таблицу employee_testing(user_id, number_test, id_question) данными тестирования."""

        try:
            data = (user_id, number_test, id_question)
            self.cursor.execute(f'INSERT INTO employee_testing(user_id, number_test, id_question) '
                                f'VALUES(?, ?, ?);', data)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def check_data(self, user_id, number_test, id_question):
        f"""Поиск совпадения. Если в таблице employee_testing есть трока с {user_id}, {number_test} и {id_question} 
        возвращает True, иначе False."""

        try:
            # data = (user_id, number_test, id_question)
            info = self.cursor.execute(f"select * from employee_testing where "
                                       f"user_id = ? and "
                                       f"number_test = ? and "
                                       f"id_question = ?", (user_id, number_test, id_question,))
            if info.fetchone() is None:  # Если записи нет
                return False
            else:  # Если запись есть
                return True
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def update_data_poll(self, name_column, set_value, user_id, number_test, id_question):
        """Заполняет таблицу employee_testing(id_answer, id_poll, id_poll_answer) данными тестирования."""

        try:
            # data = ()
            self.cursor.execute(f'UPDATE employee_testing '
                                f'SET {name_column} = ? '
                                f'WHERE user_id = ? and number_test = ? and id_question = ?',
                                (set_value, user_id, number_test, id_question,))
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def update_data_poll_option_ids(self, name_column, set_value, user_id, poll_id):
        """Заполняет таблицу employee_testing("""

        try:
            # data = ()
            self.cursor.execute(f'UPDATE employee_testing '
                                f'SET {name_column} = ? '
                                f'WHERE user_id = ? and id_poll = ?',
                                (set_value, user_id, poll_id,))
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def get_value(self, name_column, user_id, poll_id):
        """"""

        try:
            request = f'SELECT "{name_column}" ' \
                      f'FROM employee_testing ' \
                      f'WHERE user_id = "{user_id}" and id_poll = "{poll_id}"'
            self.cursor.execute(request)
            data = self.cursor.fetchone()
            self.sqlite_connection.commit()
            self.cursor.close()
            return data
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def create_data_poll(self, user_id, test_code):
        """"""

        try:
            request = f'SELECT * FROM employee_testing WHERE user_id="{user_id}" and number_test = "{test_code}"'
            self.cursor.execute(request)
            records = self.cursor.fetchall()

            data_answers = {}

            for row in records:
                id_question = row[2]
                id_answers = row[6]
                data_answers[id_question] = [id_answers]
                # print(data_answers)

            # self.cursor.close()
            return data_answers
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def get_message_poll_id(self, user_id, test_number):
        """Получить список со всеми id сообщений в рамках теста для пользователя для дальнейшего их удаления из БД."""

        try:
            list_names_column = ['id_message_poll', 'id_message', 'id_user_message', 'id_start']
            total_list = []
            for elem in list_names_column:
                request = f'SELECT "{elem}" FROM employee_testing WHERE ' \
                          f'user_id = "{user_id}" and number_test = "{test_number}"'
                self.cursor.execute(request)
                data = self.cursor.fetchall()
                for i in data:
                    total_list.append(i)

            return total_list
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    ###

    def updating_sensor_data(self, id_sensor, name_sensor, ip_host, name_host, online, last_value, last_update):
        """Обновление данных о датчиках"""

        try:
            status = self.cursor.execute(f'SELECT * FROM sensors WHERE id_sensor={id_sensor}')
            if status.fetchone() is None:  # Если датчика нет в БД
                data = (id_sensor, name_sensor, ip_host, name_host, online, last_value, last_update)
                self.cursor.execute(f'INSERT INTO sensors(id_sensor, name_sensor, ip_host, name_host, online, '
                                    f'last_value, last_update) VALUES(?, ?, ?, ?, ?, ?, ?);', data)
                self.sqlite_connection.commit()
                self.cursor.close()
            else:  # Иначе обновляем данные
                data2 = ('True', last_value, last_update, id_sensor)
                sql_update_query = 'UPDATE sensors SET online = ?, last_value = ?, last_update = ? ' \
                                   'WHERE id_sensor = ?'
                self.cursor.execute(sql_update_query, data2)
                self.sqlite_connection.commit()
                self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            # logging_event('error', str(error))

    def host_sensors_error(self, ip_host):
        try:
            sql_update_query = 'UPDATE sensors SET online = ? WHERE ip_host = ?'
            data = ('False', ip_host)
            self.cursor.execute(sql_update_query, data)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            # logging_event('error', str(error))

    def collect_statistical_information(self, user_id):
        """Добавляет +1 к счётчику активности пользователя за сегодня в таблицу users,
         в колонку activity_counter_today"""

        try:
            sql_select_query = f'SELECT activity_counter_today FROM users WHERE user_id = "{user_id}"'
            self.cursor.execute(sql_select_query)
            count = self.cursor.fetchone()
            count = count[0]
            print(f'Было {count}')

            sql_update_query = f'UPDATE users ' \
                               f'SET activity_counter_today = activity_counter_today + 1 ' \
                               f'WHERE user_id = "{user_id}"'
            print(f'Стало {count + 1}')
            self.cursor.execute(sql_update_query)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def recording_statistics(self):
        """Находит всех пользователей в таблице users, у кого активность по запросам за день больше нуля.
        Если пользователь есть в таблице statistic, обновляет ему данные, а если нет, создает новую запись и
        заполняет колонки."""

        try:
            select_user_id = 'SELECT user_id, activity_counter_today FROM users WHERE activity_counter_today > 0'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()
            # print(ids_users)

            for ids in ids_users:
                select_query = f'SELECT user_id FROM statistic WHERE user_id = {ids[0]}'
                self.cursor.execute(select_query)
                ids_users = self.cursor.fetchone()
                user_id = ids[0]
                count_today = ids[1]

                if ids_users is None:
                    insert_query = f'INSERT INTO statistic (user_id, today, all_time) ' \
                                   f'VALUES ({user_id}, {count_today}, {0})'
                    self.cursor.execute(insert_query)
                    self.sqlite_connection.commit()
                else:
                    # if count_all_time is None:
                    #     count_all_time = 0
                    update_query = f'UPDATE statistic ' \
                                   f'SET today = {count_today} ' \
                                   f'WHERE user_id = {user_id}'
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
            # self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def calculating_statistics(self):
        """Подсчитывает активность пользователей"""

        try:
            current_month = date.today().month
            yesterday_month = date.today() - timedelta(days=1)
            if current_month == yesterday_month.month:
                select_query = f'SELECT * FROM statistic'
                self.cursor.execute(select_query)
                count_today = self.cursor.fetchall()
                for row in count_today:
                    user_id = row[0]
                    count_request = row[1]
                    # count_month = row[2]
                    # count_all_time = row[3]

                    # if count_month is None:
                    #     count_month = 0
                    # else:
                    #     count_month = count_month
                    #
                    # if count_all_time is None:
                    #     count_all_time = 0
                    # else:
                    #     count_all_time = count_all_time

                    update_count_month = f'UPDATE statistic ' \
                                         f'SET month = month + {count_request}, ' \
                                         f'all_time = all_time + {count_request} ' \
                                         f'WHERE user_id = {user_id}'
                    self.cursor.execute(update_count_month)
                    self.sqlite_connection.commit()
            else:
                select_query = f'SELECT * FROM statistic'
                self.cursor.execute(select_query)
                count_today = self.cursor.fetchall()
                for row in count_today:
                    user_id = row[0]
                    update_count_month = f'UPDATE statistic SET month = 0 WHERE user_id = {user_id}'
                    self.cursor.execute(update_count_month)
                    self.sqlite_connection.commit()
            # self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def reset_count_request(self):
        """Обнуляет счетчик ежедневной активности пользователей"""

        try:
            # self.calculating_statistics()
            # time.sleep(5)
            select_query = f'SELECT * FROM statistic'
            self.cursor.execute(select_query)
            count_today = self.cursor.fetchall()
            for row in count_today:
                user_id = row[0]
                reset_count_today_users = f'UPDATE users ' \
                                          f'SET activity_counter_today = 0 ' \
                                          f'WHERE user_id = {user_id}'
                reset_count_today_statistic = f'UPDATE statistic ' \
                                              f'SET today = 0 ' \
                                              f'WHERE user_id = {user_id}'
                self.cursor.execute(reset_count_today_users)
                self.sqlite_connection.commit()
                self.cursor.execute(reset_count_today_statistic)
                self.sqlite_connection.commit()
            # self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def top_chart(self):
        """Достаёт из таблицы statistic самых активных пользователей. Возвращает текст с именами этих пользователей и
        обнуляет счётчики."""

        try:
            self.recording_statistics()
            self.calculating_statistics()
            select_data = f'SELECT * FROM statistic'
            self.cursor.execute(select_data)
            list_top_user = self.cursor.fetchall()
            list_today = {}
            list_month = {}
            list_all = {}
            for row in list_top_user:
                user_id = row[0]
                today = row[1]
                month = row[2]
                all = row[3]
                list_today[user_id] = today
                list_month[user_id] = month
                list_all[user_id] = all
            # self.cursor.close()
            # print(list_today, list_month, list_all)

            top_user_today = max(list_today)
            top_user_month = max(list_month)
            top_user_all = max(list_all)

            def get_name_user(user_id):  # noqa
                select_name = f'SELECT user_first_name, user_last_name FROM users WHERE user_id = "{user_id}"'
                self.cursor.execute(select_name)
                name_top_user = self.cursor.fetchone()
                name_top_user = ' '.join(name_top_user)
                return name_top_user

            top_user_today = get_name_user(top_user_today)
            top_user_month = get_name_user(top_user_month)
            top_user_all = get_name_user(top_user_all)

            select_user_id = 'SELECT user_id FROM users WHERE activity_counter_today > 0'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()
            print(ids_users)
            count_active_users = len(ids_users)

            end_text = f'•••Топ лидеров•••\n\n' \
                       f'• {top_user_today} лидер по количеству запросов за сегодня - {max(list_today.values())} ' \
                       f'запрос(а/ов)\n' \
                       f'• Лидер по запросам за месяц {top_user_month} - {max(list_month.values())} запрос(а/ов)\n' \
                       f'• Лидер за всё время {top_user_all} - {max(list_all.values())} запрос(а/ов)\n\n' \
                       f'Количество пользователей которые пользовались ботом за последние сутки - {count_active_users}'

            print(end_text)
            self.reset_count_request()
            self.cursor.close()
            return end_text
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))


def days_before_inventory(number):
    """Принимает на вход число и склоняет его.
    Результат - str<До предстоящей инвентаризации остался/осталось день/дня/дней>"""

    stayed = ['остался', 'осталось']
    days = ['день', 'дня', 'дней']

    if number == 0:
        return 'Сегодня инвентаризация.'
    elif number % 10 == 1 and number % 100 != 11:
        s = 0
        d = 0
        return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d] + '.'
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        s = 1
        d = 1
        return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d] + '.'
    else:
        s = 1
        d = 2
        return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d] + '.'


def number_of_events(number):
    """Принимает на вход число и склоняет его.
    Результат - str<На данный момент есть {number} запись/записи/записей. Сколько событий показать?>"""

    records = ['запись', 'записи', 'записей']

    if number == 0:
        return 'К сожалению, нет данных о предстоящих дежурствах.'
    elif number % 10 == 1 and number % 100 != 11:  # <1, 21 запись>
        r = 0
        return 'На данный момент есть ' + str(number) + ' ' + records[r] + '. Сколько событий показать?'
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):  # <3, 22 записи>
        r = 1
        return 'На данный момент есть ' + str(number) + ' ' + records[r] + '. Сколько событий показать?'
    else:  # <5, 47 записей>
        r = 2
        return 'На данный момент есть ' + str(number) + ' ' + records[r] + '. Сколько событий показать?'


def declension_day(number):
    """Принимает на вход число и склоняет слово день. Результат - str<день/дня/дней>"""

    days = ['день', 'дня', 'дней']

    if number == 0:
        return days[2]
    elif number % 10 == 1 and number % 100 != 11:
        return days[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return days[1]
    else:
        return days[2]
