import datetime
import logging
import math
import os
import random
import sqlite3
import time

import telebot

import Data

# from Data import list_command_admin, list_command_user
# from datetime import datetime, date, timedelta
#
# from Other_functions.Working_with_notifications import Notification
# from  import Notification
import src.Other_functions.Functions
from src.Other_functions import Working_with_notifications, Exchange_with_yougile


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
    """Возможные варианты записи логов - 'debug', 'info', 'warning', 'error', 'critical'.
    Пример запроса logging_event('error', str(text_error))"""

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
        end_text = end_text + can_do_it(Data.list_command_admin)  # Передать полный список доступных команд
    else:  # Если пользователь НЕ админ
        end_text = end_text + can_do_it(Data.list_command_user)  # Передать список команд доступных юзеру
    return end_text


def random_name():
    """Присылает уведомление кто сегодня закрывает сигналы"""
    if datetime.datetime.today().isoweekday() <= 5:
        list_name = ['Паша', 'Дима', 'Никита']
        rand_name = random.choice(list_name)

        phrase_list = [
            f'Случайным образом определено, что в цеху сегодня работает {rand_name}',
            f'Монетка подброшена. {rand_name} сегодня выполняет сигналы!',
            f'Беспощадный рандом определил, что сегодня {rand_name} занимается сигналами',
            f'Кручу-верчу сегодня {rand_name} главный по сигналам!',
            f'Сегодня {rand_name} повелитель сигналов',
            f'Сегодня только {rand_name} нажимает на кнопку "принять сигнал"!',
            f'Вжух, и сигналами сегодня занимается {rand_name}',
            f'Если бы на Ремите был конкурс на лучшего супер героя, то победил бы {rand_name} как '
            f'лучший человек-сигнал!',
            f'Сегодня лучший системный администратор {rand_name} спасает завод от нерешённых сигналов',
            f'Говорят, что за каждый сигнал будут давать премию! '
            f'{rand_name} рубанёт сегодня бабла! Но это не точно...',
            f'Хочешь изменить мир? Начни с завода! {rand_name} сегодня твой день! Сделай это!',
            f'Кому сегодня не фартануло тот {rand_name}. Сигналы сегодня на тебе!'
        ]
        rand_phrase = random.choice(phrase_list)

        for i in list_name:
            Data.bot.send_message(chat_id=Data.list_admins.get(i), text=rand_phrase)


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
            text_message = f'Присоединился новый пользователь. Нас уже {len(all_user_sql) + 1}!'
            logging_event(Data.way_to_log_telegram_bot, 'info', str(text_message))

            i = 0
            while i < len(all_user_sql):
                user_name = SQL().get_user_info(all_user_sql[i])
                try:
                    print(user_name)
                    Data.bot.send_message(all_user_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Data.telebot.apihelper.ApiTelegramException:
                    text_error = f'Пользователь <{user_name}> заблокировал бота!'
                    print(text_error)
                    logging_event(Data.way_to_log_telegram_bot, 'error', str(text_error))
                    self.log_out(all_user_sql[i])  # SQL().log_out(all_user_sql[i])
                i += 1
            self.cursor.execute('INSERT INTO users (user_id, user_first_name, user_last_name, username) VALUES (?, ?, '
                                '?, ?)',
                                (user_id, first_name, last_name, username))
            self.sqlite_connection.commit()
            # self.cursor.close()
            end_text = f'К боту подключился новый пользователь!\n{data_user()}\n'
            Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
            print(end_text)
        elif self.check_for_existence(user_id) is True:
            # обновление изменений данных о пользователе:
            sqlite_update_query = f'UPDATE users set user_first_name = ?, user_last_name = ?, username = ? ' \
                                  f'WHERE user_id = {user_id}'
            column_values = (first_name, last_name, username)
            self.cursor.execute(sqlite_update_query, column_values)
            self.sqlite_connection.commit()
            # self.cursor.close()
            end_text = f'Обновлены данные пользователя\n{data_user()}\n'
            # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
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
                # self.cursor.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)
                logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
            # finally:
            #     if self.sqlite_connection:
            #         self.sqlite_connection.close()

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
                # self.cursor.close()  # Вероятно из-за этой строки появлялась ошибка при регистрации новых
                # пользователей: Cannot operate on a closed cursor.
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def update_data_user(self, user_id, first_name, last_name, username):
        """Обновить данные о пользователе"""
        # user_id = message.from_user.id
        # # user_id = message.id и далее везде
        # first_name = message.from_user.first_name
        # last_name = message.from_user.last_name
        # username = message.from_user.username
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

        # online_telegram = check_online_api_telegram()
        # if online_telegram is True:
        try:
            status = self.cursor.execute(f'SELECT * FROM sensors WHERE name_sensor="{name_sensor}"')
            if status.fetchone() is None:  # Если датчика нет в БД
                # print(f'Датчика "{name_sensor}" нет в таблице')
                data = (id_sensor, name_sensor, ip_host, name_host, online, last_value, last_update)
                self.cursor.execute(f'INSERT INTO sensors(id_sensor, name_sensor, ip_host, name_host, online, '
                                    f'last_value, last_update) VALUES(?, ?, ?, ?, ?, ?, ?);', data)
                self.sqlite_connection.commit()
                self.cursor.close()
            else:  # Иначе обновляем данные
                # print(f'Датчик "{name_sensor}" есть в таблице')
                data2 = ('True', last_value, last_update, id_sensor)
                # 0.5 из-за задвоения get_data()
                if int(float(last_value)) < int(float(-100)):
                    sql_update_query = 'UPDATE sensors ' \
                                       'SET online = ?, last_value = ?, last_update = ?, ' \
                                       'detect_count = detect_count + 0.5 ' \
                                       'WHERE id_sensor = ?'
                else:
                    sql_update_query = 'UPDATE sensors ' \
                                       'SET online = ?, last_value = ?, last_update = ?, ' \
                                       'detect_count = 0 ' \
                                       'WHERE id_sensor = ?'
                self.cursor.execute(sql_update_query, data2)
                self.sqlite_connection.commit()
                self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_sensors, 'error', str(error))

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
            if user_id != Data.list_admins.get('Никита'):
                sql_select_query = f'SELECT activity_counter_today FROM users WHERE user_id = "{user_id}"'
                self.cursor.execute(sql_select_query)
                count = self.cursor.fetchone()[0]
                if count is None:  # Если значение счётчика пустое, заменить на "1"
                    sql_update_query = f'UPDATE users ' \
                                       f'SET activity_counter_today = 1 ' \
                                       f'WHERE user_id = "{user_id}"'
                    self.cursor.execute(sql_update_query)
                    self.sqlite_connection.commit()
                else:  # Иначе прибавить 1
                    sql_update_query = f'UPDATE users ' \
                                       f'SET activity_counter_today = activity_counter_today + 1 ' \
                                       f'WHERE user_id = "{user_id}"'
                    self.cursor.execute(sql_update_query)
                    self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def recording_statistics(self):
        """Находит всех пользователей в таблице users, у кого активность по запросам за день больше нуля.
        Если пользователь есть в таблице statistic, обновляет ему данные, а если нет, создает новую запись и
        заполняет колонки today и all_time в таблице statistic."""

        try:
            select_user_id = 'SELECT user_id, activity_counter_today ' \
                             'FROM users ' \
                             'WHERE activity_counter_today > 0'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()  # Список id пользователей у которых кол-во запросов больше 0
            # print(ids_users)

            for ids in ids_users:
                user_id = ids[0]

                select_query = f'SELECT user_id ' \
                               f'FROM statistic ' \
                               f'WHERE user_id = {user_id}'
                self.cursor.execute(select_query)
                ids_users = self.cursor.fetchone()

                user_id = ids[0]
                count_today = ids[1]

                if ids_users is None:
                    insert_query = f'INSERT INTO statistic (user_id, today, month, all_time) ' \
                                   f'VALUES ({user_id}, {count_today}, {0}, {0})'
                    self.cursor.execute(insert_query)
                    self.sqlite_connection.commit()
                else:
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
        """Подсчитывает активность пользователей. Если сегодня тот же месяц, что вчера, количество запросов за день
        прибавляются к количеству запросов за месяц и к количеству запросов за всё время для текущего пользователя"""

        try:
            current_month = datetime.date.today().month  # Текущий месяц
            yesterday_month = datetime.date.today() - datetime.timedelta(days=1)  # Вчерашний месяц
            if current_month == yesterday_month.month:  # Если сегодня тот же месяц что вчера
                select_query = f'SELECT * FROM statistic'  # Получаем все строки в таблице statistic
                self.cursor.execute(select_query)
                count_today = self.cursor.fetchall()
                # print(count_today)
                # print(len(count_today))
                # print(len(count_today[0]))
                for elem in count_today:  # Повторить для каждого элемента списка
                    user_id = elem[0]  # id пользователя
                    count_request_day = elem[1]  # Количество запросов за день
                    count_request_month = elem[2] + count_request_day  # Количество запросов за месяц
                    count_request_all_time = elem[3] + count_request_day  # Количество запросов за всё время

                    update_count_month = f'UPDATE statistic ' \
                                         f'SET month = {count_request_month}, all_time = {count_request_all_time} ' \
                                         f'WHERE user_id = {user_id}'
                    # print(update_count_month)
                    self.cursor.execute(update_count_month)
                    self.sqlite_connection.commit()
                    # self.cursor.close()
            else:
                select_query = f'SELECT * FROM statistic'
                self.cursor.execute(select_query)
                count_today = self.cursor.fetchall()
                for elem in count_today:
                    user_id = elem[0]
                    update_count_month = f'UPDATE statistic ' \
                                         f'SET month = 0 ' \
                                         f'WHERE user_id = {user_id}'
                    self.cursor.execute(update_count_month)
                    self.sqlite_connection.commit()
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
            self.recording_statistics()  # Заполнение таблицы statistic или ее дополнение
            self.calculating_statistics()  # Подсчет активности

            select_data = f'SELECT * FROM statistic'
            self.cursor.execute(select_data)
            list_top_user = self.cursor.fetchall()

            test_dict = {}

            for row in list_top_user:
                user_id = row[0]
                today = row[1]
                month = row[2]
                alltime = row[3]
                test_dict[user_id] = {'today': today, 'month': month, 'alltime': alltime}

            list_today = []
            list_month = []
            list_alltime = []

            for key, value in test_dict.items():
                list_today.append([value.get('today'), key])
                list_month.append([value.get('month'), key])
                list_alltime.append([value.get('alltime'), key])

            list_top_user_today = max(list_today)
            list_top_user_month = max(list_month)
            list_top_user_all = max(list_alltime)

            name_top_user_today = self.get_name_user(list_top_user_today[1])
            name_top_user_month = self.get_name_user(list_top_user_month[1])
            name_top_user_all = self.get_name_user(list_top_user_all[1])

            today_leader_name = name_top_user_today
            today_count = list_top_user_today[0]
            today_count_name = f'{today_count} {declension(today_count, "запрос", "запроса", "запросов")}'

            month_leader_name = name_top_user_month
            month_count = list_top_user_month[0]
            month_count_name = f'{month_count} {declension(month_count, "запрос", "запроса", "запросов")}'

            all_leader_name = name_top_user_all
            all_count = list_top_user_all[0]
            all_count_name = f'{all_count} {declension(all_count, "запрос", "запроса", "запросов")}'

            select_user_id = 'SELECT user_id FROM users WHERE activity_counter_today > 0'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()

            count_active_users = len(ids_users)
            average = self.average_values_active_users()

            today_count_active = f'{count_active_users} ' \
                                 f'{declension(count_active_users, "пользователь", "пользователя", "пользователей")}'

            on_average_per_day = f'{average} ' \
                                 f'{declension(average, "пользователь", "пользователя", "пользователей")}'

            if today_count == 0:
                leader_today = '• Лидера за прошедшие сутки нет :('
            else:
                leader_today = f'• Лидер за прошедшие сутки {today_leader_name} - {today_count_name}'

            end_text = f'••• Ежедневная статистика активности •••\n\n' \
                       f'{leader_today}\n' \
                       f'• Лидер за текущий месяц {month_leader_name} - {month_count_name}\n' \
                       f'• Лидер за всё время {all_leader_name} - {all_count_name}\n\n' \
                       f'За прошедшие сутки - {today_count_active}\n' \
                       f'В среднем, за день - {on_average_per_day}\n'

            print(end_text)
            self.calculating_the_average_number_of_active_users()
            self.reset_count_request()
            # self.cursor.close()
            return end_text
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def calculating_the_average_number_of_active_users(self):
        """Записывает в БД дату и кол-во пользователей использовавших бота за сегодня."""

        try:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            yesterday = yesterday.strftime('%d.%m.%Y')

            select_user_id = 'SELECT user_id FROM users WHERE activity_counter_today > 0'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()
            count = len(ids_users)

            insert_query = f'INSERT INTO user_activity_counter (date, count) ' \
                           f'VALUES ("{yesterday}", {count})'
            self.cursor.execute(insert_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def average_values_active_users(self):
        try:
            select_query = 'SELECT count ' \
                           'FROM user_activity_counter'
            self.cursor.execute(select_query)
            data = self.cursor.fetchall()

            the_amount = 0
            for elem in data:
                the_amount += elem[0]

            count_elem = len(data)
            if count_elem == 0:
                count_elem = 1
            else:
                count_elem = count_elem

            average = the_amount / count_elem
            average = math.ceil(average)  # Округление до ближайшего большего числа
            return average
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def check_status_bar(self, user_id):
        try:
            select_user_id = f'SELECT sub_bar FROM users WHERE user_id = {user_id}'
            self.cursor.execute(select_user_id)
            status_user = self.cursor.fetchone()[0]
            if status_user == 'yes':
                return True
            elif status_user == 'no':
                return False
            else:
                return 'error'
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def change_status_bar(self, user_id):
        try:
            select_user_id = f'SELECT sub_bar FROM users WHERE user_id = {user_id}'
            self.cursor.execute(select_user_id)
            user = self.cursor.fetchone()[0]
            # print(user)

            if user == 'no':
                update_query = f'UPDATE users SET sub_bar = "yes" WHERE user_id = "{user_id}"'
                self.cursor.execute(update_query)
                self.sqlite_connection.commit()
                # print('status no change to yes')
                text = 'Теперь вы подписаны на обновления барахолки. Прямо сейчас Вам станут доступны лоты, ' \
                       'которые еще не забрали.'
                count_subs_users = self.count_users()
                random_notification = [
                    f'На обновления барахолки подписался ещё один пользователь. Теперь нас {count_subs_users}!',
                    f'У нас тут пополнение. В барахолке уже {count_subs_users} '
                    f'{declension(count_subs_users, "пользователь", "пользователя", "пользователей")}!',
                    f'Барахолка пополнилась ещё на 1го пользователя. Итого {count_subs_users}.'
                ]
                rand_phrase = random.choice(random_notification)
                text_message = rand_phrase
                Working_with_notifications.Notification().notification_for_sub_baraholka(text_message)
                self.send_lots_new_sub_bar(user_id)
                return text
            elif user == 'yes':
                update_query = f'UPDATE users SET sub_bar = "no" WHERE user_id = "{user_id}"'
                self.cursor.execute(update_query)
                self.sqlite_connection.commit()
                # print('status True change to False')
                text = 'Вы больше не будете получать уведомления из барахолки.'
                return text
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def record_lot_to_DB(self, name_lot, photo_id, description):
        """Записывает данные о новых лотах"""
        try:
            today = datetime.datetime.now()
            today = today.date()

            insert_query = f'INSERT INTO lots (name, description, id_photo, date_of_public) ' \
                           f'VALUES ("{name_lot}", "{description}", "{photo_id}", "{today}")'
            self.cursor.execute(insert_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def booked_lots(self, number_lot, user_id):
        """Проверяет кол-во забронированных лотов. Если их меньше чем 3, бронирует лот, записывает в БД, обновляет
        сообщение у пользователей и возвращает 'Success', иначе возвращает текст с ошибкой."""

        try:
            count_booked = self.count_booked_lot(user_id)

            if count_booked < 3:
                select_query = f'SELECT booked FROM lots WHERE ID = {number_lot}'
                self.cursor.execute(select_query)
                status_booked = self.cursor.fetchone()[0]
                if status_booked == 'no':
                    date = datetime.datetime.today()
                    update_query = f'UPDATE lots ' \
                                   f'SET booked = "yes", booked_by_whom = {user_id}, booking_date = "{date}" ' \
                                   f'WHERE ID = {number_lot}'
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
                    self.edit_message_lots(number_lot)
                    return 'Success'
            elif count_booked >= 3:
                return 'Вы можете забронировать не более 3 лотов!'
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def count_booked_lot(self, user_id):
        """"""
        try:
            select_query = f'SELECT ID ' \
                           f'FROM lots ' \
                           f'WHERE booked_by_whom = {user_id} and confirm = "no"'
            self.cursor.execute(select_query)
            count_booked = len(self.cursor.fetchall())
            return count_booked
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def edit_message_lots(self, number_lot):
        """"""
        try:
            select_query = f'SELECT ids_message FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            dict_user_mess = self.cursor.fetchone()[0]
            dict_user_mess = eval(dict_user_mess)
            # print(dict_user_mess)
            # print(type(dict_user_mess))

            select_query = f'SELECT name FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            name_lot = self.cursor.fetchone()[0]  # Получаем название лота

            select_query = f'SELECT description FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            description_lot = self.cursor.fetchone()[0]  # Получаем описание лота

            select_query = f'SELECT booked FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            status_lot = self.cursor.fetchone()[0]  # Получаем статус лота

            select_query = f'SELECT booked_by_whom FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            booked_by_whom = self.cursor.fetchone()[0]  # Получаем user_id пользователя кто забронировал лот

            select_query = f'SELECT booking_date FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            str_booking_date = self.cursor.fetchone()[0]  # Получаем дату брони
            if str_booking_date != '':
                booking_date = datetime.datetime.strptime(str_booking_date, '%Y-%m-%d %H:%M:%S.%f')
                date_of_cancel = booking_date + datetime.timedelta(days=1)
                date_of_cancel_format = date_of_cancel.strftime("%d.%m.%Y %H:%M:%S")

            select_query = f'SELECT on_the_hands FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            on_the_hands = self.cursor.fetchone()[0]  # Получаем статус лота (на руках он или нет)

            select_query = f'SELECT confirm FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            confirm = self.cursor.fetchone()[0]  # Получаем статус подтверждения выдачи

            select_query = f'SELECT date_of_public FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            date_public = self.cursor.fetchone()[0]  # Получаем дату поста
            date = datetime.datetime.strptime(date_public, "%Y-%m-%d")
            date = date.date()
            date_public_format = date.strftime('%d.%m.%Y')

            select_query = f'SELECT status FROM lots WHERE ID = {number_lot}'
            self.cursor.execute(select_query)
            status_active_lot = self.cursor.fetchone()[0]  # Получаем статус активности лота

            ### В этом блоке проверяются посты статус которых "active". Если пост размещён более 30 дней назад, он
            ### становится неактивным у всех, в БД меняется статус на "cancel" и впредь не попадает под проверку
            if status_active_lot == 'active':
                # date_format = date.strftime('%d.%m.%Y')
                # print(date_format)
                date_today = datetime.datetime.now()
                date_today = date_today.date()
                date_today_format = date_today.strftime('%d.%m.%Y')

                dif_day = date_today - date
                dif_day = dif_day.days
                # print(dif_day)
                if dif_day > 30:
                    update_query = f'UPDATE lots ' \
                                   f'SET status = "cancel" ' \
                                   f'WHERE ID = {number_lot}'
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
                    for user_id, message_id in dict_user_mess.items():
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'#####\n' \
                                          f'Пост аннулирован {date_today_format} из-за срока давности\n' \
                                          f'#####'
                            Data.bot.edit_message_caption(chat_id=user_id,
                                                          message_id=message_id,
                                                          caption=description)

                            Data.bot.unpin_chat_message(chat_id=user_id,
                                                        message_id=message_id)
            ###

            if status_lot == 'yes' and on_the_hands == 'no':
                for user_id, message_id in dict_user_mess.items():
                    if user_id != booked_by_whom:
                        if self.check_for_admin(user_id) is True:
                            select_query = f'SELECT user_first_name, user_last_name ' \
                                           f'FROM users ' \
                                           f'WHERE user_id = {booked_by_whom}'
                            self.cursor.execute(select_query)
                            data_of_user = self.cursor.fetchone()  # Получаем данные о пользователе
                            temp_list = []
                            for elem in data_of_user:
                                if elem is not None:
                                    temp_list.append(elem)

                            full_name_user = ' '.join(temp_list)

                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'#####\n' \
                                          f'Лот зарезервирован пользователем <{full_name_user}>. ' \
                                          f'Бронирование недоступно. ' \
                                          f'Если до {date_of_cancel_format} его не заберут, ' \
                                          f'бронь аннулируется и вы сможете отложить его для себя.\n' \
                                          f'#####'
                            Data.bot.edit_message_caption(chat_id=user_id,
                                                          message_id=message_id,
                                                          caption=description)
                        else:
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'#####\n' \
                                          f'Лот зарезервирован. Бронирование недоступно. ' \
                                          f'Если до {date_of_cancel_format} его не заберут, ' \
                                          f'бронь аннулируется и вы сможете отложить его для себя.\n' \
                                          f'#####'
                            Data.bot.edit_message_caption(chat_id=user_id,
                                                          message_id=message_id,
                                                          caption=description)
                    else:
                        str_dict_cancel = str({'cancel': number_lot})
                        str_dict_sold = str({'sold': number_lot})

                        keyboard = telebot.types.InlineKeyboardMarkup()
                        button = telebot.types.InlineKeyboardButton(text='Отменить бронь',
                                                                    callback_data=str_dict_cancel)
                        button_2 = telebot.types.InlineKeyboardButton(text='Лот уже у меня',
                                                                      callback_data=str_dict_sold)
                        keyboard.add(button, button_2)

                        Data.bot.edit_message_caption(chat_id=user_id,
                                                      message_id=message_id,
                                                      caption=f'Лот №{number_lot}\n\n'
                                                              f'Название: {name_lot}\n\n'
                                                              f'Описание: {description_lot}\n\n'
                                                              f'#####\n'
                                                              f'Этот лот забронирован вами '
                                                              f'до {date_of_cancel_format}. '
                                                              f'Если забрать не успеваете, бронь аннулируется!\n'
                                                              f'#####',
                                                      reply_markup=keyboard)
            elif status_lot == 'yes' and on_the_hands == 'yes':
                for user_id, message_id in dict_user_mess.items():
                    if user_id != booked_by_whom:
                        if self.check_for_admin(user_id) is True and confirm == 'no':
                            str_dict_confirm = str({'confirm': number_lot})
                            str_dict_refute = str({'refute': number_lot})

                            keyboard = telebot.types.InlineKeyboardMarkup()
                            button = telebot.types.InlineKeyboardButton(text='Подтвердить выдачу',
                                                                        callback_data=str_dict_confirm)
                            button_2 = telebot.types.InlineKeyboardButton(text='Лот не выдан',
                                                                          callback_data=str_dict_refute)
                            keyboard.add(button, button_2)
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'#####\n' \
                                          f'Ожидает подтверждения выдачи\n' \
                                          f'#####'
                            Data.bot.edit_message_caption(chat_id=user_id,
                                                          message_id=message_id,
                                                          caption=description,
                                                          reply_markup=keyboard)
                        else:
                            if confirm == 'no':
                                description = f'Лот №{number_lot}\n\n' \
                                              f'Название: {name_lot}\n\n' \
                                              f'Описание: {description_lot}\n\n' \
                                              f'#####\n' \
                                              f'Ожидает подтверждения выдачи. Если выдача не подтвердится, ' \
                                              f'лот снова станет доступен. Следите за обновлениями!\n' \
                                              f'#####'
                                Data.bot.edit_message_caption(chat_id=user_id,
                                                              message_id=message_id,
                                                              caption=description)
                            else:
                                description = f'Лот №{number_lot}\n\n' \
                                              f'Название: {name_lot}\n\n' \
                                              f'Описание: {description_lot}\n\n' \
                                              f'#####\n' \
                                              f'Лот забрали. Он более недоступен.\n' \
                                              f'#####'
                                Data.bot.edit_message_caption(chat_id=user_id,
                                                              message_id=message_id,
                                                              caption=description)

                                Data.bot.unpin_chat_message(chat_id=user_id,
                                                            message_id=message_id)
                    else:
                        if confirm == 'no':
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'#####\n' \
                                          f'Вы указали, что забрали этот лот! Если выдача не подтвердится, ' \
                                          f'статус сменится на "Этот лот забронирован вами".\n' \
                                          f'При получении лота покажите это сообщение, оно ' \
                                          f'подтверждает, что он ЗАБРОНИРОВАН ВАМИ, а не ' \
                                          f'кем-то другим.\n' \
                                          f'ВАЖНО!\n' \
                                          f'После того как лот окажется у вас на руках, обязательно подтвердите ' \
                                          f'получение нажав кнопку "Лот уже у меня"!' \
                                          f'#####'

                            Data.bot.edit_message_caption(chat_id=user_id,
                                                          message_id=message_id,
                                                          caption=description)
                        elif confirm == 'yes':
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'#####\n' \
                                          f'Выдача лота подтверждена.\n' \
                                          f'Поздравляем с приобретением!\n' \
                                          f'#####'
                            Data.bot.edit_message_caption(chat_id=user_id,
                                                          message_id=message_id,
                                                          caption=description)

                            Data.bot.unpin_chat_message(chat_id=user_id,
                                                        message_id=message_id)
            elif status_lot == 'no':
                # print('status lot no')
                str_dict_lot = str({'lot': number_lot})
                keyboard = telebot.types.InlineKeyboardMarkup()
                button = telebot.types.InlineKeyboardButton(text='Забронировать лот',
                                                            callback_data=str_dict_lot)
                keyboard.add(button)
                for user_id, message_id in dict_user_mess.items():
                    Data.bot.edit_message_caption(chat_id=user_id,
                                                  message_id=message_id,
                                                  caption=f'Лот №{number_lot}\n\n'
                                                          f'Название: {name_lot}\n\n'
                                                          f'Описание: {description_lot}\n\n',
                                                  reply_markup=keyboard)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        except Data.telebot.apihelper.ApiTelegramException as error:
            text_error = f'Не удаётся обновить лот {number_lot} у пользователя {user_id}\n' \
                         f'{error}\n\n'
            print(text_error)

    def get_id_mes_lot(self, id_lot, user_id):
        """"""
        try:
            select_query = f'SELECT ids_message FROM lots WHERE ID = {id_lot}, booked_by_whom = {user_id}'
            self.cursor.execute(select_query)
            dict_ids = self.cursor.fetchone()[0]
            dict_ids = eval(dict_ids)
            id_message = dict_ids[user_id]
            return id_message
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def cancel_lot(self, id_lot):
        """"""
        try:
            update_query = f'UPDATE lots SET booked = "no", booked_by_whom = "", booking_date = "" WHERE ID = {id_lot}'
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def sold_lot(self, id_lot, user_id):
        """"""
        try:
            today = datetime.datetime.today()
            update_query = f'UPDATE lots ' \
                           f'SET on_the_hands = "yes", who_took_it = {user_id}, date_of_issue = "{today}", ' \
                           f'confirm = "no" ' \
                           f'WHERE ID = {id_lot}'
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def confirm_the_issue(self, id_lot):
        """Подтверждение выдачи лота. В БД обновляются данные и у всех пользователей обновляет сообщение."""

        try:
            update_query = f'UPDATE lots ' \
                           f'SET confirm = "yes" ' \
                           f'WHERE ID = {id_lot}'
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def refute_the_issue(self, id_lot):
        """Опровержение того что лот на руках"""

        try:
            update_query = f'UPDATE lots ' \
                           f'SET on_the_hands = "no", who_took_it = "", date_of_issue = "", confirm = "no" ' \
                           f'WHERE ID = {id_lot}'
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def schedule_cancel_booking(self):
        """Находит все даты броней в БД и если находит лот у которого истёк срок брони, обнуляет его и меняет текст
        сообщения у тех, кто отслеживает лот."""

        try:
            today = datetime.datetime.today()

            select_query = f'SELECT booking_date, ID ' \
                           f'FROM lots ' \
                           f'WHERE on_the_hands = "no"'  #
            self.cursor.execute(select_query)
            list_booking_date = self.cursor.fetchall()  # Список дат забронированных лотов
            for elem in list_booking_date:
                date = elem[0]
                id_lot = elem[1]
                if date != '' and date is not None:
                    dates = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
                    date_of_cancel = dates + datetime.timedelta(days=1)
                    # print(date_of_cancel)
                    if today > date_of_cancel:
                        update_query = f'UPDATE lots ' \
                                       f'SET booked = "no", booked_by_whom = 0, booking_date = "" ' \
                                       f'WHERE ID = {id_lot}'
                        self.cursor.execute(update_query)
                        self.sqlite_connection.commit()

                        self.edit_message_lots(id_lot)
                        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                              f'Бронь на лот №{id_lot} аннулирована, т.к. истёк срок брони.')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def schedule_cancel_lot(self):
        """Проверяет дату размещения поста. Если пост висит более 30 дней, лот аннулируется"""

        try:
            today = datetime.datetime.today()
            today = today.date()

            select_query = f'SELECT date_of_public, ID ' \
                           f'FROM lots ' \
                           f'WHERE status = "active"'
            self.cursor.execute(select_query)
            list_date = self.cursor.fetchall()
            for element in list_date:
                date_str = element[0]  # Дата поста str из DB
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Дата поста datetime в формате
                date = date.date()  # Дата поста без времени

                date_today = datetime.datetime.now()  # Текущая дата
                date_today = date_today.date()  # Текущая дата без времени

                dif_day = date_today - date  # Разница между датами
                dif_day = dif_day.days  # Разница между датами без времени
                # print(dif_day)

                id_lot = element[1]  # ID лота
                if dif_day > 30:
                # print(f'{dif_day} > 30')

                    self.edit_message_lots(id_lot)
                    print(f'{date_today}\n'
                          f'Лот №{id_lot} аннулирован, т.к. истёк срок.')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def schedule_updating_data_on_lots(self):
        """Актуализирует лоты у всех пользователей отталкиваясь от данных из БД"""

        try:
            select_query = f'SELECT ID ' \
                           f'FROM lots'
            self.cursor.execute(select_query)
            list_id_lots = self.cursor.fetchall()  # Полный список ID лотов
            for elem in list_id_lots:
                id_lot = elem[0]
                self.edit_message_lots(id_lot)
                time.sleep(1)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def count_users(self):
        """Подсчитывает кол-во подписчиков барахолки"""

        try:
            select_query = f'SELECT user_id ' \
                           f'FROM users ' \
                           f'WHERE sub_bar = "yes"'
            self.cursor.execute(select_query)
            list_booking_date = self.cursor.fetchall()
            count_sub = len(list_booking_date)
            return count_sub
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def test(self):
        select_query = f'SELECT user_id, today FROM statistic'  # Получаем все строки в таблице statistic
        self.cursor.execute(select_query)
        count_today = self.cursor.fetchall()
        print(count_today)
        for row in count_today:  # Повторить для каждой строки
            user_id = row[0]
            count_request = row[1]
            print(f'юзер {user_id} - счётчик {count_request}')

    def get_name_attr_class_or_insert_button(self, name_button, value_button):
        print(f'get_or_insert_button: {name_button}, {value_button}')
        select_query = f'SELECT name_attr_class FROM buttons WHERE value_button = "{value_button}"'  #
        self.cursor.execute(select_query)
        name_attr_class = self.cursor.fetchone()
        if name_attr_class is not None and name_attr_class != '':
            func = name_attr_class[0]
            print(func)
            # name_func = func().__class__.__name__
            # print(name_func)
            # eval(func)
            return func
        else:
            insert_query = f'INSERT INTO buttons (name_button, value_button) ' \
                           f'VALUES ("{name_button}", "{value_button}")'
            self.cursor.execute(insert_query)
            self.sqlite_connection.commit()

    # def save_data_sensor_to_BD(self, dict_data):
    #     """"""
    #
    #     try:
    #
    #         # update_query = f'UPDATE lots ' \
    #         #                f'SET on_the_hands = "no", who_took_it = "", date_of_issue = "", confirm = "no" ' \
    #         #                f'WHERE ID = {id_lot}'
    #         # self.cursor.execute(update_query)
    #         # self.sqlite_connection.commit()
    #         # self.edit_message_lots(id_lot)
    #     except sqlite3.Error as error:
    #         print("Ошибка при работе с SQLite", error)
    #         logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def send_lots_new_sub_bar(self, user_id):
        """Доставляет новым подписчикам барахолки лоты которые ещё не забрали"""

        try:
            select_query = f'SELECT * ' \
                           f'FROM lots ' \
                           f'WHERE confirm = "no"'
            self.cursor.execute(select_query)
            lots_not_hand = self.cursor.fetchall()
            for lots in lots_not_hand:
                number_lot = lots[0]
                name_lot = lots[1]
                description_lot = lots[2]
                id_photo = lots[3]
                booked = lots[4]
                booked_by_whom = lots[5]
                booking_date = lots[6]
                on_the_hands = lots[7]
                who_took_it = lots[8]
                date_of_issue = lots[9]
                ids_message = eval(lots[10])
                confirm = lots[11]

                # data_lot = [number_lot, name_lot, description_lot, id_photo, booked, booked_by_whom, booking_date,
                #             on_the_hands, who_took_it, date_of_issue, ids_message, confirm]

                if user_id not in ids_message.keys():  # Если у пользователя отсутствует лот
                    # print('user not found')
                    if booked == 'no':  # Если лот не забронирован
                        callback_data = src.Other_functions.Functions.pack_in_callback_data('lot', number_lot)
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        button = telebot.types.InlineKeyboardButton(text='Забронировать лот',
                                                                    callback_data=callback_data)
                        keyboard.add(button)

                        caption = f'Лот №{number_lot}\n\n' \
                                  f'Название: {name_lot}\n\n' \
                                  f'Описание: {description_lot}\n\n'

                        message_id = Data.bot.send_photo(chat_id=user_id,
                                                         caption=caption,
                                                         photo=id_photo,
                                                         reply_markup=keyboard).message_id

                        Data.bot.pin_chat_message(chat_id=user_id,
                                                  message_id=message_id)  # Закрепляет сообщение у пользователя

                        ids_message[user_id] = message_id
                    elif booked == 'yes':  # Если лот забронирован
                        if on_the_hands == 'no':  # Если лот не на руках
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'### Лот зарезервирован. Бронирование недоступно. ' \
                                          f'Если до {booking_date} его не заберут, ' \
                                          f'бронь аннулируется и вы сможете отложить его для себя. ###'
                            message_id = Data.bot.send_photo(chat_id=user_id,
                                                             caption=description,
                                                             photo=id_photo).message_id

                            Data.bot.pin_chat_message(chat_id=user_id,
                                                      message_id=message_id)  # Закрепляет сообщение у пользователя

                            ids_message[user_id] = message_id
                        elif on_the_hands == 'yes':  # Если лот на руках
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'### Ожидает подтверждения выдачи. Если выдача не подтвердится, ' \
                                          f'лот снова станет доступен. Следите за обновлениями! ###'
                            message_id = Data.bot.send_photo(chat_id=user_id,
                                                             caption=description,
                                                             photo=id_photo).message_id

                            Data.bot.pin_chat_message(chat_id=user_id,
                                                      message_id=message_id)  # Закрепляет сообщение у пользователя

                            ids_message[user_id] = message_id

                    update_query = f'UPDATE lots ' \
                                   f'SET ids_message = "{ids_message}" ' \
                                   f'WHERE ID = {number_lot}'
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
                else:
                    # print('user in dict')
                    pass
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def check_top_byers(self):
        """Возвращает строку с топ 3 самыми жадными пользователями барахолки"""

        select_query = f'SELECT who_took_it ' \
                       f'FROM lots ' \
                       f'WHERE confirm = "yes"'
        self.cursor.execute(select_query)
        list_byers = self.cursor.fetchall()

        temp_list = []

        for user_ids in list_byers:
            if user_ids[0] is not None:
                temp_list.append(user_ids[0])

        temp_dict = {}

        for i in temp_list:
            if i not in temp_dict.keys():
                temp_dict[i] = 1
            else:
                temp_dict[i] += 1

        sorted_dict = {}
        sorted_keys = sorted(temp_dict, key=temp_dict.get, reverse=True)

        for w in sorted_keys:
            sorted_dict[w] = temp_dict[w]

        while len(sorted_dict) > 3:
            numb_elem = len(sorted_dict) - 1
            sorted_dict.pop(list(sorted_dict)[numb_elem])

        temp_list_2 = []

        for i in sorted_dict.keys():
            select_query = f'SELECT user_first_name, user_last_name ' \
                           f'FROM users ' \
                           f'WHERE user_id = {i}'
            self.cursor.execute(select_query)
            tuple_data_user = self.cursor.fetchall()

            list_data_user = []

            for u in tuple_data_user[0]:
                if u is not None:
                    list_data_user.append(u)

            temp_list_data_user = [sorted_dict.get(i), ' '.join(list_data_user), i]
            temp_list_2.append(temp_list_data_user)

        return temp_list_2

    def create_string_top_byers_all_time(self):
        """Формирует строку с топ 3 пользователей барахолки по кол-ву лотов на руках"""

        top_list = self.check_top_byers()

        first_place_name = top_list[0][1]
        first_place_count = f'{top_list[0][0]} {declension(top_list[0][0], "лот", "лота", "лотов")}'

        second_place_name = top_list[1][1]
        second_place_count = f'{top_list[1][0]} {declension(top_list[1][0], "лот", "лота", "лотов")}'

        third_place_name = top_list[2][1]
        third_place_count = f'{top_list[2][0]} {declension(top_list[2][0], "лот", "лота", "лотов")}'

        title_text = f'••• Рейтинг пользователей барахолки •••\n' \
                     f'За всё время, у этих пользователей на руках оказалось больше всего лотов:\n' \
                     f'1е место: {first_place_name} - {first_place_count}\n' \
                     f'2е место: {second_place_name} - {second_place_count}\n' \
                     f'3е место: {third_place_name} - {third_place_count}\n\n' \
                     f'Данный рейтинг формируется каждый месяц.'

        return title_text

    def top_user(self):
        """Вычисляет топ 3 самых активных пользователей по запросам к боту, далее формирует топ 3 подписчика
        барахолки у которых больше всего лотов на руках. Если в списках есть совпадения по user_id, объединяет
        показатели по следующей формуле: {кол-во запросов}+{кол-во лотов на руках * 10}, а если совпадения нет -
        просто добавляет в общий список ТОПов. Далее этот общий список сортируется по рейтингу и отсекаются
        все пользователи после 3 элемента. Итог - список списков [рейтинг, user_id]"""

        try:
            top_list_byers = self.check_top_byers()
            for byers in top_list_byers:
                byers.pop(1)

            select_user_id = 'SELECT user_id, all_time FROM statistic'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()

            top_list_active_users = []

            for row in ids_users:
                top_list_active_users.append([row[1], row[0]])

            top_list_active_users.sort(reverse=True)

            while len(top_list_active_users) > 3:
                top_list_active_users.pop(-1)

            list_top = []

            for active in top_list_active_users:
                for byers in top_list_byers:
                    if active[1] in byers:
                        print(f'{byers[1]} - {active[0]}+{byers[0]}*10={active[0] + (byers[0] * 10)}')
                        list_top.append([active[0] + (byers[0] * 10), active[1]])
                        top_list_active_users.pop(top_list_active_users.index(active))
                        top_list_byers.pop(top_list_byers.index(byers))

            for elem in top_list_active_users:
                list_top.append(elem)

            for i in top_list_byers:
                list_top.append([i[0] * 10, i[1]])

            list_top.sort(reverse=True)

            while len(list_top) > 3:
                list_top.pop(-1)

            print(list_top)

            return list_top
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def get_name_user(self, user_id):  # noqa
        select_name = f'SELECT user_first_name, user_last_name ' \
                      f'FROM users ' \
                      f'WHERE user_id = "{user_id}"'
        self.cursor.execute(select_name)
        name_top_user = self.cursor.fetchone()
        # print(name_top_user)
        full_name = []
        for elem in name_top_user:
            if elem is not None:
                full_name.append(elem)

        if len(full_name) > 1:
            name_top_user = ' '.join(full_name)
            return name_top_user
        else:
            return name_top_user[0]

    def get_list_faulty_sensors(self):
        """Проверяет в БД таблицу sensors, колонку detect_count.
        Если счётчик равен 60, присылает уведомление разработчику."""
        try:
            select_query = f'SELECT name_sensor ' \
                           f'FROM sensors ' \
                           f'WHERE detect_count = 60'
            self.cursor.execute(select_query)
            list_sensors = self.cursor.fetchall()

            detected_list = []
            for elem in list_sensors:
                detected_list.append(elem[0])
            # print(detected_list)

            if len(detected_list) > 1:
                nl = '\n'
                end_text = f'Более часа нет ответа от этих датчиков:\n\n' \
                           f'{nl.join(detected_list)}'
                # print(end_text)
            elif len(detected_list) == 1:
                end_text = f'Более часа нет ответа от датчика <{detected_list}>'

            if len(detected_list) != 0:
                # print(detected_list)
                Data.bot.send_message(chat_id=Data.list_admins.get('Никита'),
                                      text=end_text)

                for elem in detected_list:
                    title = f'Неисправен датчик <{elem}>'
                    # print(title)
                    Exchange_with_yougile.post_task_to_column_sensors(title_text=title)
                    time.sleep(1)

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)


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


def declension(number, one, two, five):
    """Принимает на вход число, название объекта с численностью 1, 2 и 5.
    Например, при входных данных <21, 'день', 'дня', 'дней'> результатом будет являться <день>"""

    if number == 0:
        return five
    elif number % 10 == 1 and number % 100 != 11:
        return one
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return two
    else:
        return five


def pack_in_callback_data(key, value):
    dict_callback = {key: value}
    string_dict = str(dict_callback)
    return string_dict


# def pack_in_callback_data(type_button, key, value):
#     dict_callback = {type_button: {key: value}}
#     string_dict = str(dict_callback)
#     return string_dict


def string_to_dict(string_dict):
    my_dict = eval(string_dict)
    return my_dict


# for i in range(0, 101):
#     print(f"{i} {declension(i, 'лот', 'лота', 'лотов')}")


def check_online_api_telegram():
    """Проверяет на доступность api.telegram.org. Если доступен, вернёт True, иначе - False."""

    hostname = "api.telegram.org"  # example
    response = os.system("ping -c 1 " + hostname)

    # and then check the response...
    if response == 0:
        # print(hostname, 'is up!')
        return True
    else:
        # print(hostname, 'is down!')
        return False
