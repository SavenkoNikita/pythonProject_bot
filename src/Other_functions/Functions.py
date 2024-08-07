import datetime
import logging
import math
import os
import random
import sqlite3
import time

import telebot

from src.Body_bot import Secret
from src.Other_functions import Working_with_notifications, Exchange_with_yougile


def get_key(user_name):
    """Проверяет среди словаря есть ли в нём имя{user_name} и возвращает соответствующий id_telegram"""

    # key = 'Имя не найдено или человек не относится к дежурным. Error Other_function.get_key.'
    for keys, v in Secret.user_data.items():
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

    logging_event(Secret.way_to_log_sensors, condition, text_log)


def logging_scheduler(condition, text_log):
    """Записывает логи schedule. На вход принимает записываемый в файл текст. Возможные варианты записи логов -
    'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Secret.way_to_log_scheduler, condition, text_log)


def logging_telegram_bot(condition, text_log):
    """Записывает логи работы бота. На вход принимает записываемый в файл текст. Возможные варианты записи логов -
    'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Secret.way_to_log_telegram_bot, condition, text_log)


def logging_file_processing(condition, text_log):
    """Записывает логи работы с файлом. На вход принимает записываемый в файл текст. Возможные варианты записи логов -
    'debug', 'info', 'warning', 'error', 'critical' """

    logging_event(Secret.way_to_log_file_processing, condition, text_log)


def can_do_it(x):
    """Перечисляет строка за строкой всё что есть в списке с переводом строки."""

    cd = ('\n'.join(map(str, x)))
    return cd


def can_help(user_id):
    """Формирует список доступных команд для пользователя в зависимости админ он или нет."""

    end_text = f'Вот что я умею:\n'
    check_admin = SQL().check_for_admin(user_id)
    if check_admin is True:  # Если пользователь админ
        end_text = end_text + can_do_it(Secret.list_command_admin)  # Передать полный список доступных команд
    else:  # Если пользователь НЕ админ
        end_text = end_text + can_do_it(Secret.list_command_user)  # Передать список команд доступных юзеру
    return end_text


def name_hero():
    """Присылает уведомление кто на этой неделе закрывает сигналы"""
    if datetime.datetime.today().isoweekday() <= 1:
        from src.Other_functions import File_processing
        name = File_processing.Working_with_a_file('Дежурный').read_file()[0][2]  # Имя ближайшего дежурного

        phrase_list = [
            f'Монетка подброшена. {name} на этой неделе выполняет сигналы!',
            f'Беспощадный график определил, что на этой неделе {name} занимается сигналами!',
            f'Кручу-верчу на этой неделе {name} главный по сигналам!',
            f'На этой неделе {name} повелитель сигналов!',
            f'На этой неделе только {name} нажимает на кнопку "Принять сигнал"!',
            f'Вжух, и сигналами на этой неделе занимается {name}!',
            f'На этой неделе лучший системный администратор {name} спасает завод от нерешённых сигналов!',
            f'Хочешь изменить мир? Начни с Ремита! {name} на этой неделе всё держится на тебе! Сделай это!',
            f'Кому на этой неделе не фартануло тот {name}. Сигналы на тебе!'
        ]

        rand_phrase = random.choice(phrase_list)

        for key, value in Secret.list_admins.items():
            Secret.bot.send_message(chat_id=value, text=rand_phrase)


class SQL:
    """Проверка, добавление, обновление и удаление данных о пользователях"""

    def __init__(self):
        self.sqlite_connection = sqlite3.connect(Secret.way_sql, check_same_thread=False, timeout=10)
        self.cursor = self.sqlite_connection.cursor()
        self.current_year = datetime.datetime.now().year

    def check_verify_in_ERP(self, user_id):
        """Проверка на то, прошёл ли пользователь верификацию в 1С. Возвращает True или False"""

        try:
            if self.check_for_existence(user_id) is True:
                status_ERP = self.cursor.execute(f'SELECT * FROM users WHERE verify_erp="yes" and user_id="{user_id}"')
                if status_ERP.fetchone() is None:  # Если пользователь не верифицирован в 1С
                    return False
                else:  # Если пользователь верифицирован в 1С
                    return True
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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

            count_users = len(all_user_sql) + 1
            list_phrase = [f'Присоединился новый пользователь. Нас уже {count_users}!',
                           f'Счётчик пользователей нашего бота пополнился на одного. Итого: {count_users}',
                           f'У нас пополнение! К {count_users - 1} прибавился ещё пользователь',
                           f'Число {count_users} вам ни о чём не говорит? Подскажу, к нам присоединился ещё один'
                           f' пользователь!']
            text_message = random.choice(list_phrase)
            logging_event(Secret.way_to_log_telegram_bot, 'info', str(text_message))

            i = 0
            while i < len(all_user_sql):
                user_name = SQL().get_user_info(all_user_sql[i])
                try:
                    print(user_name)
                    Secret.bot.send_message(all_user_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Secret.telebot.apihelper.ApiTelegramException:
                    text_error = f'Пользователь <{user_name}> заблокировал бота!'
                    print(text_error)
                    logging_event(Secret.way_to_log_telegram_bot, 'error', str(text_error))
                    self.log_out(all_user_sql[i])  # SQL().log_out(all_user_sql[i])
                i += 1
            self.cursor.execute(f'INSERT INTO users (user_id, user_first_name, user_last_name, username) '
                                f'VALUES ("{user_id}", "{first_name}", "{last_name}", "{username}"')
            self.sqlite_connection.commit()
            # self.cursor.close()
            end_text = f'К боту подключился новый пользователь!\n{data_user()}\n'
            Secret.bot.send_message(chat_id=Secret.list_admins.get('Никита'), text=end_text)
            print(end_text)
        elif self.check_for_existence(user_id) is True:
            # обновление изменений данных о пользователе:
            sqlite_update_query = (f'UPDATE users '
                                   f'SET user_first_name = "{first_name}", user_last_name = "{last_name}", '
                                   f'username = "{username}" '
                                   f'WHERE user_id = "{user_id}"')
            # column_values = (first_name, last_name, username)
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()
            # self.cursor.close()
            end_text = f'Обновлены данные пользователя\n{data_user()}\n'
            # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
            # print(end_text)
        else:
            end_text = 'Пользователь уже есть в базе данных!\n' + data_user() + '\n'
            Secret.bot.send_message(chat_id=Secret.list_admins.get('Никита'), text=end_text)
            print(end_text)

        return end_text

    def update_sqlite_table(self, status, user_id, column_name):
        """Обновление статуса пользователя в SQL"""
        if self.check_for_existence(user_id) is True:
            try:
                self.cursor.execute(f'UPDATE users '
                                    f'SET {column_name} = "{status}" '
                                    f'WHERE user_id = "{user_id}"')
                # self.cursor.execute(f"Update users set {column_name} = {status} where user_id = {user_id}")
                self.sqlite_connection.commit()
                print("Запись успешно обновлена")
                # self.cursor.close()
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)
                logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
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
                logging_event(Secret.way_to_log_telegram_bot, 'info', try_message)
                self.cursor.execute(f'DELETE from {table_name_DB} '
                                    f'WHERE user_id = "{user_id}"')
                self.sqlite_connection.commit()
                # self.cursor.close()  # Вероятно из-за этой строки появлялась ошибка при регистрации новых
                # пользователей: Cannot operate on a closed cursor.
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def update_data_user(self, user_id, first_name, last_name, username):
        """Обновить данные о пользователе"""
        if self.check_for_existence(user_id) is True:
            try:
                self.cursor.execute(f'SELECT * '
                                    f'FROM users '
                                    f'WHERE user_id = "{user_id}"')
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
                logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
            # finally:
            #     if self.sqlite_connection:
            #         self.sqlite_connection.close()

    def get_user_info(self, user_id, table_name='users', column_name='user_id'):
        """Получить данные о пользователе"""
        try:
            self.cursor.execute(f'SELECT * '
                                f'FROM {table_name} '
                                f'WHERE {column_name} = "{user_id}"')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def get_a_user_sticker_from_the_database(self, user_id):
        """Получить стикер пользователя"""
        try:
            request = (f'SELECT sticker '
                       f'FROM users '
                       f'WHERE user_id = "{user_id}"')
            self.cursor.execute(request)
            sticker = self.cursor.fetchone()[0]
            if sticker is not None:
                return sticker
            else:
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def get_list_users(self):
        """Получить список всех пользователей"""
        try:
            sql_select_query = ('SELECT * '
                                'FROM users')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
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
            request = (f'SELECT * '
                       f'FROM {table_DB} '
                       f'WHERE user_id = "{user_id}" and {column_name} = "{status}"')
            self.cursor.execute(request)
            user = self.cursor.fetchone()
            if user is not None:
                return True
            else:
                return False
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def create_list_users(self, column_name_DB, column_meaning, name_table_DB='users'):
        """Формирует список пользователей с подходящими параметрами. Например, список id_user которые подписаны на
        уведомления. На вход принимает имя колонки из БД и значение ячейки. Результат list[user_id]."""

        try:
            info = self.cursor.execute(f'SELECT * '
                                       f'FROM {name_table_DB} '
                                       f'WHERE {column_name_DB} = "{column_meaning}"')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def get_mess_id(self, user_id):
        """Проверяет есть ли message_id в tracking_sensor_defroster и если есть возвращает его"""

        try:
            request = (f'SELECT * '
                       f'FROM tracking_sensor_defroster '
                       f'WHERE user_id = "{user_id}"')
            self.cursor.execute(request)
            row = self.cursor.fetchone()
            if row is not None:
                return row[1]
            else:
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def add_user_by_table(self, user_id, column_name, status, name_table_DB):
        f"""Если пользователь подписан на {column_name} и отсутствует в {name_table_DB}, добавляет его."""

        try:
            if self.check_status_DB(user_id, column_name, status) is True:
                if self.check_for_existence(user_id, name_table_DB) is False:
                    self.cursor.execute(f'INSERT INTO {name_table_DB} (user_id, message_id) '
                                        f'VALUES ("{user_id}", "None")')
                    self.sqlite_connection.commit()
                    self.cursor.close()
                    print(f'Пользователь {user_id} успешно добавлен в таблицу {name_table_DB}')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def update_mess_id_by_table(self, user_id, message_id, table_name_DB, name_column_in_table_users):
        f"""В таблице {table_name_DB} обновляет пользователю {user_id} значение {message_id}"""

        try:
            if self.check_status_DB(user_id, name_column_in_table_users, 'yes') is True:
                if self.check_for_existence(user_id, table_name_DB) is True:
                    # обновление изменений данных о сообщении:
                    sqlite_update_query = (f'UPDATE {table_name_DB} '
                                           f'SET message_id="{message_id}" '
                                           f'WHERE user_id="{user_id}"')
                    self.cursor.execute(sqlite_update_query)
                    self.sqlite_connection.commit()
                    self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def get_dict(self, table_name_DB):
        """Получить список user_id и message_id"""

        try:
            request = (f'SELECT * '
                       f'FROM {table_name_DB}')
            self.cursor.execute(request)
            row = self.cursor.fetchall()
            return row
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        # finally:
        #     if self.sqlite_connection:
        #         self.sqlite_connection.close()

    def talk(self, text_message):
        """Ищет в БД ответ на вопрос. Принимает текст сообщения. Если есть ответ, возвращает его,
        а если нет, возвращает None"""

        try:
            request = (f'SELECT * '
                       f'FROM talk '
                       f'WHERE question = "{text_message}"')
            self.cursor.execute(request)
            row = self.cursor.fetchone()
            if row is not None:
                return row[1]
            else:
                self.insert_data_speak_DB(text_message)
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def insert_data_speak_DB(self, text_message):
        """Добавляет ответ на вопрос в БД."""

        try:
            self.cursor.execute(f'INSERT INTO talk (question, answer) '
                                f'VALUES ("{text_message}", "None")')
            self.sqlite_connection.commit()
            self.cursor.close()
            print(f'Запись {text_message} успешно добавлена в таблицу talk')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def update_answer_speak_DB(self, question, answer):
        """"""

        try:
            sqlite_update_query = (f'UPDATE talk '
                                   f'SET answer = "{answer}" '
                                   f'WHERE question = "{question}"')
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def count_not_answer(self, count=0):
        """Считает кол-во вопросов без ответа. Результат - число."""

        try:
            self.cursor.execute('SELECT * '
                                'FROM talk')
            row = self.cursor.fetchall()
            for rows in row:
                # print(rows[1])
                if rows[1] is None:
                    count += 1

            # count_none_rows = f'На данный момент есть {count} вопросов без ответа.'
            return count
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def search_not_answer(self):
        """Находит первый вопрос без ответа. Результат - текст вопроса."""

        try:
            self.cursor.execute('SELECT * '
                                'FROM talk')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def update_data_in_table_SQL(self, name_table, set_name_column, set_value_column, user_id):

        """Обновляет данные в таблице {name_table},
        устанавливает в колонке {set_name_column} значение {set_value_column} пользователю {user_id}"""

        try:
            sqlite_update_query = (f'UPDATE {name_table} '
                                   f'SET {set_name_column} = "{set_value_column}" '
                                   f'WHERE user_id = "{user_id}"')
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def select_data(self, name_table):
        """"""

        try:
            self.cursor.execute(f'SELECT * '
                                f'FROM {name_table}')
            records = self.cursor.fetchall()
            self.cursor.close()
            return records
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite: ", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    #  Работа с тестированием сотрудников
    def insert_data(self, user_id, number_test, id_question):
        """Заполняет таблицу employee_testing(user_id, number_test, id_question) данными тестирования."""

        try:
            self.cursor.execute(f'INSERT INTO employee_testing (user_id, number_test, id_question) '
                                f'VALUES ("{user_id}", "{number_test}", "{id_question}")')
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def check_data(self, user_id, number_test, id_question):
        f"""Поиск совпадения. Если в таблице employee_testing есть трока с {user_id}, {number_test} и {id_question} 
        возвращает True, иначе False."""

        try:
            info = self.cursor.execute(f'SELECT * '
                                       f'FROM employee_testing '
                                       f'WHERE user_id = "{user_id}" and '
                                       f'number_test = "{number_test}" and '
                                       f'id_question = "{id_question}"')
            if info.fetchone() is None:  # Если записи нет
                return False
            else:  # Если запись есть
                return True
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def update_data_poll(self, name_column, set_value, user_id, number_test, id_question):
        """Заполняет таблицу employee_testing(id_answer, id_poll, id_poll_answer) данными тестирования."""

        try:
            self.cursor.execute(f'UPDATE employee_testing '
                                f'SET {name_column} = "{set_value}" '
                                f'WHERE user_id = "{user_id}" and '
                                f'number_test = "{number_test}" and '
                                f'id_question = "{id_question}"')
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def update_data_poll_option_ids(self, name_column, set_value, user_id, poll_id):
        """Заполняет таблицу employee_testing("""

        try:
            self.cursor.execute(f'UPDATE employee_testing '
                                f'SET {name_column} = "{set_value}" '
                                f'WHERE user_id = "{user_id}" and '
                                f'id_poll = "{poll_id}"')
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def create_data_poll(self, user_id, test_code):
        """"""

        try:
            request = (f'SELECT * '
                       f'FROM employee_testing '
                       f'WHERE user_id = "{user_id}" and number_test = "{test_code}"')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    ###

    def updating_sensor_data(self, id_sensor, name_sensor, ip_host, name_host, online, last_value, last_update):
        """Обновление данных о датчиках"""

        # online_telegram = check_online_api_telegram()
        # if online_telegram is True:
        try:
            status = self.cursor.execute(f'SELECT * '
                                         f'FROM sensors '
                                         f'WHERE id_sensor = "{id_sensor}" AND ip_host = "{ip_host}"')
            if status.fetchone() is None:  # Если датчика нет в БД
                # print(f'Датчика "{name_sensor}" нет в таблице')
                # data = (id_sensor, name_sensor, ip_host, name_host, online, last_value, last_update)
                self.cursor.execute(f'INSERT INTO sensors(id_sensor, name_sensor, ip_host, name_host, online, '
                                    f'last_value, last_update) '
                                    f'VALUES("{id_sensor}", "{name_sensor}", "{ip_host}", "{name_host}", "{online}", '
                                    f'"{last_value}", "{last_update}")')
                self.sqlite_connection.commit()
                # self.cursor.close()
            else:  # Иначе обновляем данные
                # 0.5 из-за задвоения get_data()
                if int(float(last_value)) < int(float(-100)) or int(float(100)) < int(float(last_value)):
                    sql_update_query = (f'UPDATE sensors '
                                        f'SET online = "{True}", last_value = "{last_value}", '
                                        f'last_update = "{last_update}", detect_count = detect_count + 0.5, '
                                        f'name_sensor = "{name_sensor}" '
                                        f'WHERE id_sensor = "{id_sensor}" AND ip_host = "{ip_host}"')
                else:
                    sql_update_query = (f'UPDATE sensors '
                                        f'SET online = "{True}", last_value = "{last_value}", '
                                        f'last_update = "{last_update}", '
                                        f'detect_count = 0, name_sensor = "{name_sensor}" '
                                        f'WHERE id_sensor = "{id_sensor}" AND ip_host = "{ip_host}"')
                    self.cursor.execute(sql_update_query)
                    self.sqlite_connection.commit()

                    select_query = self.cursor.execute(f'SELECT id_task_yougile '
                                                       f'FROM sensors '
                                                       f'WHERE id_sensor = "{id_sensor}" AND ip_host = "{ip_host}"')
                    id_task_yougile = select_query.fetchone()[0]

                    if id_task_yougile != '':
                        # print(f'<{id_task_yougile}> != ""')
                        Exchange_with_yougile.YouGile().delete_task(id_task_yougile)

                        sql_update_query = (f'UPDATE sensors '
                                            f'SET id_task_yougile = "" '
                                            f'WHERE id_sensor = "{id_sensor}" AND ip_host = "{ip_host}"')
                        self.cursor.execute(sql_update_query)
                        self.sqlite_connection.commit()

                self.cursor.execute(sql_update_query)
                self.sqlite_connection.commit()
                # self.cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_sensors, 'error', str(error))

    def host_sensors_error(self, ip_host):
        try:
            sql_update_query = (f'UPDATE sensors '
                                f'SET online = "False" '
                                f'WHERE ip_host = "{ip_host}"')
            self.cursor.execute(sql_update_query)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            # logging_event('error', str(error))

    def collect_statistical_information(self, user_id):
        """Добавляет +1 к счётчику активности пользователя за сегодня в таблицу users,
         в колонку activity_counter_today"""

        try:
            if user_id != Secret.list_admins.get('Никита'):
                sql_select_query = (f'SELECT activity_counter_today '
                                    f'FROM users '
                                    f'WHERE user_id = "{user_id}"')
                self.cursor.execute(sql_select_query)
                count = self.cursor.fetchone()[0]
                if count is None:  # Если значение счётчика пустое, заменить на "1"
                    sql_update_query = (f'UPDATE users '
                                        f'SET activity_counter_today = 1 '
                                        f'WHERE user_id = "{user_id}"')
                    self.cursor.execute(sql_update_query)
                    self.sqlite_connection.commit()
                else:  # Иначе прибавить 1
                    sql_update_query = (f'UPDATE users '
                                        f'SET activity_counter_today = activity_counter_today + 1 '
                                        f'WHERE user_id = "{user_id}"')
                    self.cursor.execute(sql_update_query)
                    self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def recording_statistics(self):
        """Находит всех пользователей в таблице users, у кого активность по запросам за день больше нуля.
        Если пользователь есть в таблице statistic, обновляет ему данные, а если нет, создает новую запись и
        заполняет колонки today и all_time в таблице statistic."""

        try:
            select_user_id = ('SELECT user_id, activity_counter_today '
                              'FROM users '
                              'WHERE activity_counter_today > 0')
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()  # Список id пользователей у которых кол-во запросов больше 0

            for ids in ids_users:
                user_id = ids[0]

                select_query = (f'SELECT user_id '
                                f'FROM statistic '
                                f'WHERE user_id = "{user_id}"')
                self.cursor.execute(select_query)
                ids_users = self.cursor.fetchone()

                user_id = ids[0]
                count_today = ids[1]

                if ids_users is None:
                    insert_query = (f'INSERT INTO statistic (user_id, today, month, all_time) '
                                    f'VALUES ("{user_id}", "{count_today}", "{0}", "{0}")')
                    self.cursor.execute(insert_query)
                    self.sqlite_connection.commit()
                else:
                    update_query = (f'UPDATE statistic '
                                    f'SET today = {count_today} '
                                    f'WHERE user_id = "{user_id}"')
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def calculating_statistics(self):
        """Подсчитывает активность пользователей. Если сегодня тот же месяц, что вчера, количество запросов за день
        прибавляются к количеству запросов за месяц и к количеству запросов за всё время для текущего пользователя"""

        try:
            current_month = datetime.date.today().month  # Текущий месяц
            yesterday_month = datetime.date.today() - datetime.timedelta(days=1)  # Вчерашний месяц
            if current_month == yesterday_month.month:  # Если сегодня тот же месяц, что вчера
                select_query = (f'SELECT * '
                                f'FROM statistic')  # Получаем все строки в таблице statistic
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

                    update_count_month = (f'UPDATE statistic '
                                          f'SET month = "{count_request_month}", all_time = "{count_request_all_time}" '
                                          f'WHERE user_id = "{user_id}"')
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
                    update_count_month = (f'UPDATE statistic '
                                          f'SET month = 0 '
                                          f'WHERE user_id = "{user_id}"')
                    self.cursor.execute(update_count_month)
                    self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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
                reset_count_today_users = (f'UPDATE users '
                                           f'SET activity_counter_today = 0 '
                                           f'WHERE user_id = "{user_id}"')
                reset_count_today_statistic = (f'UPDATE statistic '
                                               f'SET today = 0 '
                                               f'WHERE user_id = "{user_id}"')
                self.cursor.execute(reset_count_today_users)
                self.sqlite_connection.commit()
                self.cursor.execute(reset_count_today_statistic)
                self.sqlite_connection.commit()
            # self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def calculating_the_average_number_of_active_users(self):
        """Записывает в БД дату и кол-во пользователей использовавших бота за сегодня."""

        try:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            yesterday = yesterday.strftime('%d.%m.%Y')

            select_user_id = 'SELECT user_id FROM users WHERE activity_counter_today > 0'
            self.cursor.execute(select_user_id)
            ids_users = self.cursor.fetchall()
            count = len(ids_users)

            insert_query = (f'INSERT INTO user_activity_counter (date, count) '
                            f'VALUES ("{yesterday}", "{count}")')
            self.cursor.execute(insert_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def average_values_active_users(self):
        try:
            select_query = ('SELECT count '
                            'FROM user_activity_counter')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def check_status_bar(self, user_id):
        try:
            select_user_id = (f'SELECT sub_bar '
                              f'FROM users '
                              f'WHERE user_id = "{user_id}"')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def change_status_bar(self, user_id):
        try:
            select_user_id = (f'SELECT sub_bar '
                              f'FROM users '
                              f'WHERE user_id = "{user_id}"')
            self.cursor.execute(select_user_id)
            user = self.cursor.fetchone()[0]
            # print(user)

            if user == 'no':
                update_query = (f'UPDATE users '
                                f'SET sub_bar = "yes" '
                                f'WHERE user_id = "{user_id}"')
                self.cursor.execute(update_query)
                self.sqlite_connection.commit()
                # print('status no change to yes')
                text = ('Теперь вы подписаны на обновления барахолки. Если есть активные лоты, они прямо сейчас '
                        'станут Вам доступны.')
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
                update_query = (f'UPDATE users '
                                f'SET sub_bar = "no" '
                                f'WHERE user_id = "{user_id}"')
                self.cursor.execute(update_query)
                self.sqlite_connection.commit()
                # print('status True change to False')
                text = 'Вы больше не будете получать уведомления из барахолки.'
                return text
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def booked_lots(self, number_lot, user_id):
        """Проверяет кол-во забронированных лотов. Если их меньше чем 3, бронирует лот, записывает в БД, обновляет
        сообщение у пользователей и возвращает 'Success', иначе возвращает текст с ошибкой."""

        try:
            count_booked = self.count_booked_lot(user_id)
            print(count_booked)

            if count_booked < 3:
                select_query = (f'SELECT booked '
                                f'FROM lots '
                                f'WHERE ID = "{number_lot}"')
                self.cursor.execute(select_query)
                status_booked = self.cursor.fetchone()[0]
                print(status_booked)
                if status_booked == 'no':
                    date = datetime.datetime.today()
                    update_query = (f'UPDATE lots '
                                    f'SET booked = "yes", booked_by_whom = "{user_id}", booking_date = "{date}" '
                                    f'WHERE ID = "{number_lot}"')
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
                    self.edit_message_lots(number_lot)
                    return 'Success'
            elif count_booked >= 3:
                return 'Вы можете забронировать не более 3 лотов!'
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def count_booked_lot(self, user_id):
        """"""
        try:
            select_query = (f'SELECT ID '
                            f'FROM lots '
                            f'WHERE booked_by_whom = "{user_id}" and confirm = "no"')
            self.cursor.execute(select_query)
            count_booked = len(self.cursor.fetchall())
            return count_booked
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    # def edit_message_lots(self, number_lot):
    #     """"""
    #     try:
    #         # select_query = (f'SELECT ids_message '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # dict_user_mess = self.cursor.fetchone()[0]  # Словарь user.id:message.id
    #         # dict_user_mess = eval(dict_user_mess)
    #         # # print(f'Словарь user.id:message.id = {dict_user_mess}')
    #         #
    #         # select_query = (f'SELECT name '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # name_lot = self.cursor.fetchone()[0]  # Получаем название лота
    #         # # print(f'Название лота = {name_lot}')
    #         #
    #         # select_query = (f'SELECT description '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # description_lot = self.cursor.fetchone()[0]  # Получаем описание лота
    #         # # print(f'Описание лота = {description_lot}')
    #         #
    #         # select_query = (f'SELECT booked '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # status_lot = self.cursor.fetchone()[0]  # Получаем статус лота
    #         # # print(f'Статус лота = {status_lot}')
    #         #
    #         # select_query = (f'SELECT booked_by_whom '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # booked_by_whom = self.cursor.fetchone()[0]  # Получаем user_id пользователя кто забронировал лот
    #         # # print(f'id пользователя кто забронировал лот = {booked_by_whom}')
    #         #
    #         # select_query = (f'SELECT booking_date '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # str_booking_date = self.cursor.fetchone()[0]  # Получаем дату брони
    #         # # print(f'Дата брони = {str_booking_date}')
    #         #
    #         # date_of_cancel_format = ''
    #         # if str_booking_date != '':
    #         #     booking_date = datetime.datetime.strptime(str_booking_date, '%Y-%m-%d %H:%M:%S.%f')
    #         #     date_of_cancel = booking_date + datetime.timedelta(days=1)
    #         #     date_of_cancel_format = date_of_cancel.strftime("%d.%m.%Y %H:%M:%S")
    #         #
    #         # select_query = (f'SELECT on_the_hands '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # on_the_hands = self.cursor.fetchone()[0]  # Получаем статус лота (на руках он или нет)
    #         # # print(f'Статус лота (на руках он или нет) = {on_the_hands}')
    #         #
    #         # select_query = (f'SELECT confirm '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # confirm = self.cursor.fetchone()[0]  # Получаем статус подтверждения выдачи
    #         # # print(f'Статус подтверждения выдачи = {confirm}')
    #         #
    #         # select_query = (f'SELECT date_of_public '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # date_public = self.cursor.fetchone()[0]  # Получаем дату поста
    #         # date = date_public
    #         # # print(f'Дата поста = {date}')
    #         #
    #         # select_query = (f'SELECT status '
    #         #                 f'FROM lots '
    #         #                 f'WHERE ID = "{number_lot}"')
    #         # self.cursor.execute(select_query)
    #         # status_active_lot = self.cursor.fetchone()[0]  # Получаем статус активности лота
    #         # print(f'Статус лота = {status_active_lot}')
    #
    #         # В этом блоке проверяются посты статус которых "active". Если пост размещён более 30 дней назад, он
    #         # становится неактивным у всех, в БД меняется статус на "cancel" и впредь не попадает под проверку
    #         # if status_active_lot == 'active':
    #         #     date_format = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    #         #     today = datetime.datetime.now().date()
    #         #
    #         #     dif_day = today - date_format
    #         #     dif_day = dif_day.days
    #         #     if dif_day > 30:
    #         #         update_query = (f'UPDATE lots '
    #         #                         f'SET status = "cancel" '
    #         #                         f'WHERE ID = "{number_lot}"')
    #         #         self.cursor.execute(update_query)
    #         #         self.sqlite_connection.commit()
    #         # elif status_active_lot == 'cancel':
    #         #     date_today = datetime.datetime.now()
    #         #     date_today_day = date_today.date()
    #         #     date_today_format = date_today_day.strftime('%d.%m.%Y')
    #         #
    #         #     for user_id, message_id in dict_user_mess.items():
    #         #         description = f'Лот №{number_lot}\n\n' \
    #         #                       f'Название: {name_lot}\n\n' \
    #         #                       f'Описание: {description_lot}\n\n' \
    #         #                       f'#####\n' \
    #         #                       f'Пост аннулирован {date_today_format} из-за срока давности\n' \
    #         #                       f'#####'
    #         #         Secret.bot.edit_message_caption(chat_id=user_id,
    #         #                                         message_id=message_id,
    #         #                                         caption=description)
    #         #
    #         #         Secret.bot.unpin_chat_message(chat_id=user_id,
    #         #                                       message_id=message_id)
    #         #         # print(f'Лот №{number_lot}: у пользователя {user_id} обновлено сообщение {message_id}')
    #         #         # continue
    #
    #         if status_lot == 'yes' and on_the_hands == 'no':
    #             for user_id, message_id in dict_user_mess.items():
    #                 if user_id != booked_by_whom:
    #                     if self.check_for_admin(user_id) is True:
    #                         select_query = (f'SELECT user_first_name, user_last_name '
    #                                         f'FROM users '
    #                                         f'WHERE user_id = "{booked_by_whom}"')
    #                         self.cursor.execute(select_query)
    #                         data_of_user = self.cursor.fetchone()  # Получаем данные о пользователе
    #                         temp_list = []
    #                         for elem in data_of_user:
    #                             if elem is not None:
    #                                 temp_list.append(elem)
    #
    #                         full_name_user = ' '.join(temp_list)
    #
    #                         description = f'Лот №{number_lot}\n\n' \
    #                                       f'Название: {name_lot}\n\n' \
    #                                       f'Описание: {description_lot}\n\n' \
    #                                       f'#####\n' \
    #                                       f'Лот зарезервирован пользователем <{full_name_user}>. ' \
    #                                       f'Бронирование недоступно. ' \
    #                                       f'Если до {date_of_cancel_format} его не заберут, ' \
    #                                       f'бронь аннулируется и вы сможете отложить его для себя.\n' \
    #                                       f'#####'
    #                         Secret.bot.edit_message_caption(chat_id=user_id,
    #                                                         message_id=message_id,
    #                                                         caption=description)
    #                 #     else:
    #                 #         description = f'Лот №{number_lot}\n\n' \
    #                 #                       f'Название: {name_lot}\n\n' \
    #                 #                       f'Описание: {description_lot}\n\n' \
    #                 #                       f'#####\n' \
    #                 #                       f'Лот зарезервирован. Бронирование недоступно. ' \
    #                 #                       f'Если до {date_of_cancel_format} его не заберут, ' \
    #                 #                       f'бронь аннулируется и вы сможете отложить его для себя.\n' \
    #                 #                       f'#####'
    #                 #         Secret.bot.edit_message_caption(chat_id=user_id,
    #                 #                                         message_id=message_id,
    #                 #                                         caption=description)
    #                 # else:
    #                     # str_dict_cancel = str({'cancel': number_lot})
    #                     # str_dict_sold = str({'sold': number_lot})
    #                     #
    #                     # keyboard = telebot.types.InlineKeyboardMarkup()
    #                     # button = telebot.types.InlineKeyboardButton(text='Отменить бронь',
    #                     #                                             callback_data=str_dict_cancel)
    #                     # button_2 = telebot.types.InlineKeyboardButton(text='Лот уже у меня',
    #                     #                                               callback_data=str_dict_sold)
    #                     # keyboard.add(button, button_2)
    #                     #
    #                     # Secret.bot.edit_message_caption(chat_id=user_id,
    #                     #                                 message_id=message_id,
    #                     #                                 caption=f'Лот №{number_lot}\n\n'
    #                     #                                         f'Название: {name_lot}\n\n'
    #                     #                                         f'Описание: {description_lot}\n\n'
    #                     #                                         f'#####\n'
    #                     #                                         f'Этот лот забронирован вами '
    #                     #                                         f'до {date_of_cancel_format}. '
    #                     #                                         f'Если забрать не успеваете, бронь аннулируется!\n'
    #                     #                                         f'#####',
    #                     #                                 reply_markup=keyboard)
    #         # elif status_lot == 'yes' and on_the_hands == 'yes':
    #         #     for user_id, message_id in dict_user_mess.items():
    #         #         if user_id != booked_by_whom:
    #         #             if self.check_for_admin(user_id) is True and confirm == 'no':
    #                         # str_dict_confirm = str({'confirm': number_lot})
    #                         # str_dict_refute = str({'refute': number_lot})
    #                         #
    #                         # keyboard = telebot.types.InlineKeyboardMarkup()
    #                         # button = telebot.types.InlineKeyboardButton(text='Подтвердить выдачу',
    #                         #                                             callback_data=str_dict_confirm)
    #                         # button_2 = telebot.types.InlineKeyboardButton(text='Лот не выдан',
    #                         #                                               callback_data=str_dict_refute)
    #                         # keyboard.add(button, button_2)
    #                         description = f'Лот №{number_lot}\n\n' \
    #                                       f'Название: {name_lot}\n\n' \
    #                                       f'Описание: {description_lot}\n\n' \
    #                                       f'#####\n' \
    #                                       f'Ожидает подтверждения выдачи\n' \
    #                                       f'#####'
    #                         Secret.bot.edit_message_caption(chat_id=user_id,
    #                                                         message_id=message_id,
    #                                                         caption=description,
    #                                                         reply_markup=keyboard)
    #                     # else:
    #                         # if confirm == 'no':
    #                         #     description = f'Лот №{number_lot}\n\n' \
    #                         #                   f'Название: {name_lot}\n\n' \
    #                         #                   f'Описание: {description_lot}\n\n' \
    #                         #                   f'#####\n' \
    #                         #                   f'Ожидает подтверждения выдачи. Если выдача не подтвердится, ' \
    #                         #                   f'лот снова станет доступен. Следите за обновлениями!\n' \
    #                         #                   f'#####'
    #                         #     Secret.bot.edit_message_caption(chat_id=user_id,
    #                         #                                     message_id=message_id,
    #                         #                                     caption=description)
    #                         # else:
    #                 #             description = f'Лот №{number_lot}\n\n' \
    #                 #                           f'Название: {name_lot}\n\n' \
    #                 #                           f'Описание: {description_lot}\n\n' \
    #                 #                           f'#####\n' \
    #                 #                           f'Лот забрали. Он более недоступен.\n' \
    #                 #                           f'#####'
    #                 #             Secret.bot.edit_message_caption(chat_id=user_id,
    #                 #                                             message_id=message_id,
    #                 #                                             caption=description)
    #                 #
    #                 #             Secret.bot.unpin_chat_message(chat_id=user_id,
    #                 #                                           message_id=message_id)
    #                 # else:
    #                     # if confirm == 'no':
    #                     #     description = f'Лот №{number_lot}\n\n' \
    #                     #                   f'Название: {name_lot}\n\n' \
    #                     #                   f'Описание: {description_lot}\n\n' \
    #                     #                   f'#####\n' \
    #                     #                   f'Вы указали, что забрали этот лот! Если выдача не подтвердится, ' \
    #                     #                   f'статус сменится на "Этот лот забронирован вами".\n' \
    #                     #                   f'При получении лота покажите это сообщение, оно ' \
    #                     #                   f'подтверждает, что он ЗАБРОНИРОВАН ВАМИ, а не ' \
    #                     #                   f'кем-то другим.\n' \
    #                     #                   f'ВАЖНО!\n' \
    #                     #                   f'После того как лот окажется у вас на руках, обязательно подтвердите ' \
    #                     #                   f'получение нажав кнопку "Лот уже у меня"!' \
    #                     #                   f'#####'
    #                     #
    #                     #     Secret.bot.edit_message_caption(chat_id=user_id,
    #                     #                                     message_id=message_id,
    #                     #                                     caption=description)
    #                     # elif confirm == 'yes':
    #                     #     description = f'Лот №{number_lot}\n\n' \
    #                     #                   f'Название: {name_lot}\n\n' \
    #                     #                   f'Описание: {description_lot}\n\n' \
    #                     #                   f'#####\n' \
    #                     #                   f'Выдача лота подтверждена.\n' \
    #                     #                   f'Поздравляем с приобретением!\n' \
    #                     #                   f'#####'
    #                     #     Secret.bot.edit_message_caption(chat_id=user_id,
    #                     #                                     message_id=message_id,
    #                     #                                     caption=description)
    #                     #
    #                     #     Secret.bot.unpin_chat_message(chat_id=user_id,
    #                     #                                   message_id=message_id)
    #         # elif status_lot == 'no':
    #         #     # print('status lot no')
    #         #     str_dict_lot = str({'lot': number_lot})
    #         #     keyboard = telebot.types.InlineKeyboardMarkup()
    #         #     button = telebot.types.InlineKeyboardButton(text='Забронировать лот',
    #         #                                                 callback_data=str_dict_lot)
    #         #     keyboard.add(button)
    #     #         for user_id, message_id in dict_user_mess.items():
    #     #             Secret.bot.edit_message_caption(chat_id=user_id,
    #     #                                             message_id=message_id,
    #     #                                             caption=f'Лот №{number_lot}\n\n'
    #     #                                                     f'Название: {name_lot}\n\n'
    #     #                                                     f'Описание: {description_lot}\n\n',
    #     #                                             reply_markup=keyboard)
    #     # except sqlite3.Error as error:
    #     #     print("Ошибка при работе с SQLite", error)
    #     #     logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
    #     #     pass
    #     # except Secret.telebot.apihelper.ApiTelegramException as error:
    #     #     text_error = f'Не удаётся обновить лот {number_lot} у пользователя {user_id}'
    #     #     response = error.result_json
    #     #     # print(response)
    #     #     status = response.get('ok')
    #     #     if status is not True:
    #     #         # print('status not True')
    #     #         description = response.get('description')
    #     #         reason = description
    #     #         if error.error_code == 400:
    #     #             if description == ('Bad Request: message is not modified: specified new message content and '
    #     #                                'reply markup are exactly the same as a current content and reply markup '
    #     #                                'of the message'):
    #     #                 reason = 'Сообщение не изменено т.к. нет изменений.'
    #     #                 pass
    #     #             elif description == 'Bad Request: message to edit not found':
    #     #                 reason = 'Сообщения с таким id не существует.'
    #     #                 del dict_user_mess[user_id]
    #     #                 update_ids_for_lot = (f'UPDATE lots '
    #     #                                       f'SET ids_message = "{dict_user_mess}"'
    #     #                                       f'WHERE ID = "{number_lot}"')
    #     #                 self.cursor.execute(update_ids_for_lot)
    #     #                 self.sqlite_connection.commit()
    #     #                 self.edit_message_lots(number_lot=number_lot)
    #     #             elif description == 'Bad Request: chat not found':
    #     #                 reason = f'Боту неизвестен чат с пользователем {user_id}'
    #     #                 del dict_user_mess[user_id]
    #     #                 update_ids_for_lot = (f'UPDATE lots '
    #     #                                       f'SET ids_message = "{dict_user_mess}"'
    #     #                                       f'WHERE ID = "{number_lot}"')
    #     #                 self.cursor.execute(update_ids_for_lot)
    #     #                 self.sqlite_connection.commit()
    #     #                 self.edit_message_lots(number_lot=number_lot)
    #     #             elif description == 'Forbidden: bot was blocked by the user':
    #     #                 reason = f'Пользователь {user_id} заблокировал бота'
    #     #                 del dict_user_mess[user_id]
    #     #                 update_ids_for_lot = (f'UPDATE lots '
    #     #                                       f'SET ids_message = "{dict_user_mess}"'
    #     #                                       f'WHERE ID = "{number_lot}"')
    #     #                 self.cursor.execute(update_ids_for_lot)
    #     #                 self.sqlite_connection.commit()
    #     #                 self.edit_message_lots(number_lot=number_lot)
    #     #
    #     #         answer_message = f'{self.edit_message_lots.__name__}\n{text_error}\n{reason}'
    #     #         print(answer_message)
    #     #
    #     #     # del dict_user_mess[user_id]
    #     #     # update_ids_for_lot = (f'UPDATE lots '
    #     #     #                       f'SET ids_message = "{dict_user_mess}"'
    #     #     #                       f'WHERE ID = "{number_lot}"')
    #     #     # self.cursor.execute(update_ids_for_lot)
    #     #     # self.sqlite_connection.commit()
    #     #     # self.edit_message_lots(number_lot=number_lot)

    def get_id_mes_lot(self, id_lot, user_id):
        """"""
        try:
            select_query = (f'SELECT ids_message '
                            f'FROM lots '
                            f'WHERE ID = "{id_lot}", booked_by_whom = "{user_id}"')
            self.cursor.execute(select_query)
            dict_ids = self.cursor.fetchone()[0]
            dict_ids = eval(dict_ids)
            id_message = dict_ids[user_id]
            return id_message
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def cancel_lot(self, id_lot):
        """"""
        try:
            update_query = (f'UPDATE lots '
                            f'SET booked = "no", booked_by_whom = "", booking_date = "", on_the_hands = "no", '
                            f'who_took_it = "", date_of_issue = "" '
                            f'WHERE ID = "{id_lot}"')
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def sold_lot(self, id_lot, user_id):
        """"""
        try:
            today = datetime.datetime.today()
            update_query = (f'UPDATE lots '
                            f'SET on_the_hands = "yes", who_took_it = "{user_id}", date_of_issue = "{today}", '
                            f'confirm = "no" '
                            f'WHERE ID = "{id_lot}"')
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def confirm_the_issue(self, id_lot):
        """Подтверждение выдачи лота. В БД обновляются данные и у всех пользователей обновляет сообщение."""

        try:
            update_query = (f'UPDATE lots '
                            f'SET confirm = "yes" '
                            f'WHERE ID = "{id_lot}"')
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def refute_the_issue(self, id_lot):
        """Опровержение того что лот на руках"""

        try:
            update_query = (f'UPDATE lots '
                            f'SET on_the_hands = "no", who_took_it = "", date_of_issue = "", confirm = "no" '
                            f'WHERE ID = "{id_lot}"')
            self.cursor.execute(update_query)
            self.sqlite_connection.commit()
            self.edit_message_lots(id_lot)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def schedule_cancel_booking(self):
        """Находит все даты броней в БД и если находит лот у которого истёк срок брони, обнуляет его и меняет текст
        сообщения у тех, кто отслеживает лот."""

        try:
            today = datetime.datetime.today()

            select_query = (f'SELECT booking_date, ID '
                            f'FROM lots '
                            f'WHERE on_the_hands = "no"')  #
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
                        update_query = (f'UPDATE lots '
                                        f'SET booked = "no", booked_by_whom = 0, booking_date = "" '
                                        f'WHERE ID = "{id_lot}"')
                        self.cursor.execute(update_query)
                        self.sqlite_connection.commit()

                        self.edit_message_lots(id_lot)
                        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                              f'Бронь на лот №{id_lot} аннулирована, т.к. истёк срок брони.')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def schedule_cancel_lot(self):
        """Проверяет дату размещения поста. Если пост висит более 30 дней, лот аннулируется"""

        try:
            # today = datetime.datetime.today()
            # today = today.date()

            select_query = (f'SELECT date_of_public, ID '
                            f'FROM lots '
                            f'WHERE status = "active"')
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
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def schedule_updating_data_on_lots(self):
        """Актуализирует лоты у всех пользователей отталкиваясь от данных из БД"""

        try:
            select_query = f'SELECT ID FROM lots'
            self.cursor.execute(select_query)
            list_id_lots = self.cursor.fetchall()  # Полный список ID лотов
            for elem in list_id_lots:
                id_lot = elem[0]
                self.edit_message_lots(id_lot)
                time.sleep(1)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def count_users(self):
        """Подсчитывает кол-во подписчиков барахолки"""

        try:
            select_query = (f'SELECT user_id '
                            f'FROM users '
                            f'WHERE sub_bar = "yes"')
            self.cursor.execute(select_query)
            list_booking_date = self.cursor.fetchall()
            count_sub = len(list_booking_date)
            return count_sub
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    # def test(self):
    #     select_query = f'SELECT user_id, today FROM statistic'  # Получаем все строки в таблице statistic
    #     self.cursor.execute(select_query)
    #     count_today = self.cursor.fetchall()
    #     # print(count_today)
    #     for row in count_today:  # Повторить для каждой строки
    #         user_id = row[0]
    #         count_request = row[1]
    #         # print(f'юзер {user_id} - счётчик {count_request}')

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
            select_query = (f'SELECT * '
                            f'FROM lots '
                            f'WHERE confirm = "no"')
            self.cursor.execute(select_query)
            lots_not_hand = self.cursor.fetchall()
            for lots in lots_not_hand:
                number_lot = lots[0]
                name_lot = lots[1]
                description_lot = lots[2]
                id_photo = lots[3]
                booked = lots[4]
                # booked_by_whom = lots[5]
                booking_date = lots[6]
                on_the_hands = lots[7]
                # who_took_it = lots[8]
                # date_of_issue = lots[9]
                ids_message = eval(lots[10])
                # confirm = lots[11]

                # data_lot = [number_lot, name_lot, description_lot, id_photo, booked, booked_by_whom, booking_date,
                #             on_the_hands, who_took_it, date_of_issue, ids_message, confirm]

                if user_id not in ids_message.keys():  # Если у пользователя отсутствует лот
                    # print('user not found')
                    if booked == 'no':  # Если лот не забронирован
                        callback_data = pack_in_callback_data('lot', number_lot)
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        button = telebot.types.InlineKeyboardButton(text='Забронировать лот',
                                                                    callback_data=callback_data)
                        keyboard.add(button)

                        caption = f'Лот №{number_lot}\n\n' \
                                  f'Название: {name_lot}\n\n' \
                                  f'Описание: {description_lot}\n\n'

                        message_id = Secret.bot.send_photo(chat_id=user_id,
                                                           caption=caption,
                                                           photo=id_photo,
                                                           reply_markup=keyboard).message_id

                        Secret.bot.pin_chat_message(chat_id=user_id,
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
                            message_id = Secret.bot.send_photo(chat_id=user_id,
                                                               caption=description,
                                                               photo=id_photo).message_id

                            Secret.bot.pin_chat_message(chat_id=user_id,
                                                        message_id=message_id)  # Закрепляет сообщение у пользователя

                            ids_message[user_id] = message_id
                        elif on_the_hands == 'yes':  # Если лот на руках
                            description = f'Лот №{number_lot}\n\n' \
                                          f'Название: {name_lot}\n\n' \
                                          f'Описание: {description_lot}\n\n' \
                                          f'### Ожидает подтверждения выдачи. Если выдача не подтвердится, ' \
                                          f'лот снова станет доступен. Следите за обновлениями! ###'
                            message_id = Secret.bot.send_photo(chat_id=user_id,
                                                               caption=description,
                                                               photo=id_photo).message_id

                            Secret.bot.pin_chat_message(chat_id=user_id,
                                                        message_id=message_id)  # Закрепляет сообщение у пользователя

                            ids_message[user_id] = message_id

                    update_query = (f'UPDATE lots '
                                    f'SET ids_message = "{ids_message}" '
                                    f'WHERE ID = "{number_lot}"')
                    self.cursor.execute(update_query)
                    self.sqlite_connection.commit()
                else:
                    # print('user in dict')
                    pass
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def check_top_byers(self):
        """Возвращает строку с топ 3 самыми жадными пользователями барахолки"""

        select_query = (f'SELECT who_took_it '
                        f'FROM lots '
                        f'WHERE confirm = "yes"')
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
            select_query = (f'SELECT user_first_name, user_last_name '
                            f'FROM users '
                            f'WHERE user_id = "{i}"')
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
        показатели по следующей формуле: {активность за месяц} * {количество забранных лотов}, а если совпадения нет -
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
                        """Коэффициент считается по формуле:
                        {активность за месяц} * {количество забранных лотов}"""
                        if active[0] > 0:
                            count_active = active[0]
                        else:
                            count_active = 1

                        name_user = byers[1]
                        user_id = active[1]
                        counter_purchased_lots = byers[0]

                        rating = count_active * counter_purchased_lots

                        print(f'{name_user}:\n'
                              f'{count_active}*{counter_purchased_lots}={rating}')

                        list_top.append([rating, user_id])
                        top_list_active_users.pop(top_list_active_users.index(active))
                        top_list_byers.pop(top_list_byers.index(byers))

            for elem in top_list_active_users:
                list_top.append(elem)

            for i in top_list_byers:
                list_top.append([i[0], i[1]])

            list_top.sort(reverse=True)

            while len(list_top) > 3:
                list_top.pop(-1)

            # print(list_top)

            return list_top
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def get_name_user(self, user_id):  # noqa
        select_name = (f'SELECT user_first_name, user_last_name '
                       f'FROM users '
                       f'WHERE user_id = "{user_id}"')
        self.cursor.execute(select_name)
        name_top_user = self.cursor.fetchone()
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
            # print(f'Старт {self.get_list_faulty_sensors.__name__}')
            select_query = (f'SELECT name_sensor '
                            f'FROM sensors '
                            f'WHERE detect_count = 60')
            self.cursor.execute(select_query)
            list_sensors = self.cursor.fetchall()  # Список совпадений

            detected_list = []
            for elem in list_sensors:
                detected_list.append(elem[0])

            # print(detected_list)

            end_text = 'Заглушка'

            if len(detected_list) > 1:  # Если список не пуст
                nl = '\n'
                end_text = f'Более часа нет ответа от этих датчиков:\n\n' \
                           f'{nl.join(detected_list)}'
            elif len(detected_list) == 1:
                name_sensor = detected_list[0]
                end_text = f'Более часа нет ответа от датчика <{name_sensor}>'
            # else:
            #     print(f'Список с неисправными датчиками пуст:\n'
            #           f'{list_sensors}')

            if len(detected_list) != 0:
                # nl = '\n'
                data_list = self.get_dict('observers_for_faulty_sensors')
                # print(data_list)

                list_users = []
                if len(data_list) != 0:
                    for users in data_list:
                        # print(users)
                        user_id = int(users[0])
                        # print(users[0])
                        list_users.append(user_id)

                if len(list_users) != 0:
                    for element in list_users:
                        try:
                            Secret.bot.send_message(chat_id=element,
                                                    text=end_text)
                        except Secret.telebot.apihelper.ApiTelegramException:
                            text_error = f'Пользователь {element} заблокировал бота!'
                            print(text_error)
                            self.log_out(element)

                for name_faulty_sensor in detected_list:
                    title = f'Больше часа нет ответа от датчика <{name_faulty_sensor}>'
                    log_text = f'{self.get_list_faulty_sensors.__name__}()\n' \
                               f'В YouGile в колонку "Контроль температур" добавлена задача:\n' \
                               f'{title}\n\n'
                    # id_task_yougile = Exchange_with_yougile.post_task_to_column_sensors(title_text=title)
                    id_task_yougile = Exchange_with_yougile.YouGile().post_task(title_task=title,
                                                                                column_task=Secret.column_termosensors)

                    # Secret.bot.send_message(chat_id=Secret.list_admins.get('Никита'),
                    #                         text=log_text)
                    time.sleep(1)
                    if id_task_yougile is not None:
                        print(log_text)
                        print(id_task_yougile)
                        sql_update_query = (f'UPDATE sensors '
                                            f'SET id_task_yougile = "{id_task_yougile}" '
                                            f'WHERE name_sensor = "{name_faulty_sensor}"')
                        self.cursor.execute(sql_update_query)
                        self.sqlite_connection.commit()

        except sqlite3.Error as error:
            error_message = f'{self.get_list_faulty_sensors.__name__}\n' \
                            f'Ошибка при работе с SQLite: <{error}>'
            print(error_message)
            Secret.bot.send_message(chat_id=Secret.list_admins.get('Никита'),
                                    text=error_message)

    def registration_secret_santa(self, user_id, user_name):
        """Регистрация участников в новогоднем обмене подарками"""
        try:
            select_query = f'SELECT nickname FROM secret_santa_{self.current_year}'
            self.cursor.execute(select_query)
            list_nickname = self.cursor.fetchall()  # Список никнеймов уже присутствующих в игре ТС

            # print(list_nickname)
            #
            # # nickname = random.choice(Secret.list_nicknames)
            select_query = f'SELECT proposal FROM creative_nick_NY WHERE approval = 1'
            self.cursor.execute(select_query)
            list_nicknames = self.cursor.fetchall()  # Список всех одобренных псевдонимов для ТС
            update_list_nicknames = []
            for lists in list_nicknames:
                update_list_nicknames.append(lists[0])
            nickname = random.choice(update_list_nicknames)

            if list_nickname is not None:
                for elements in list_nickname:
                    nickname = random.choice(update_list_nicknames)
                    if nickname in list_nickname:
                        update_list_nicknames.pop(nickname)
                    else:
                        nickname = nickname

            select_query_user_id = (f'SELECT user_id '
                                    f'FROM secret_santa_{self.current_year} '
                                    f'WHERE user_id = "{user_id}"')
            self.cursor.execute(select_query_user_id)
            user_id_in_sql = self.cursor.fetchone()  # Проверка юзера на наличие в таблице secret_santa_{current_year}
            # print(user_id_in_sql)

            if user_id_in_sql is None:  # Если юзера нет - создаёт запись
                insert_query = (f'INSERT INTO secret_santa_{self.current_year} (user_id, user_name, nickname) '
                                f'VALUES ("{user_id}", "{user_name}", "{nickname}")')
                self.cursor.execute(insert_query)
                self.sqlite_connection.commit()
            # else:
            #     print('Пользователь уже зарегистрирован')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def selecting_opponent_secret_santa(self):
        """Подбор оппонента для жеребьёвки подарков"""
        try:
            select_query = (f'SELECT user_id, good_gift, bad_gift, nickname, gift_from '
                            f'FROM secret_santa_{self.current_year}')
            self.cursor.execute(select_query)
            data_list = self.cursor.fetchall()

            positive_result = ('Привет! Тайный Санта уже записал всех участников и их пожелания. Настало время узнать '
                               'кто же выпал тебе.')

            negative_result = ('Привет! Тайный Санта уже записал всех участников и их пожелания. Количество '
                               'участников оказалось нечётным и тебе не досталось оппонента. Но не расстраивайся, '
                               'тебя под ёлкой тоже будет ждать подарок!')

            link_picture = ('https://sun9-55.userapi.com/impg/p8pV3a19CGm4FKAZWn0vZRu8ERimXP5KG-_Nig/yC8XilHLD4M.jpg'
                            '?size=833x1080&quality=95&sign=4d1ad4ae55d9d281a0db19c03e5049da&c_uniq_tag'
                            '=yz0eMUncEIgkLyv1UkIO41arT2jYmluE_YfHe0Yowa4&type=album')

            list_reg_nickname = []
            for lists in data_list:
                list_reg_nickname.append(lists[3])

            for element in data_list:
                while len(data_list) >= 1 or len(data_list) == 0:
                    gift_from = random.choice(list_reg_nickname)
                    # print(gift_from)
                    user_id = element[0]
                    nick_name = element[3]
                    if gift_from != nick_name:
                        update_query = (f'UPDATE secret_santa_{self.current_year} '
                                        f'SET gift_from = "{gift_from}" '
                                        f'WHERE user_id = "{user_id}"')
                        self.cursor.execute(update_query)
                        self.sqlite_connection.commit()
                        time.sleep(1)
                        list_reg_nickname.remove(gift_from)
                        break
                    elif len(list_reg_nickname) == 1 and gift_from == nick_name:
                        # print(f'Пользователю {data_list[0][3]} не досталось пары')
                        Secret.bot.send_message(chat_id=Secret.list_admins.get('Никита'),
                                                text=f'Пользователю {nick_name} не досталось пары при распределении '
                                                     f'в Secret_santa')
                        break

            self.cursor.execute(select_query)
            update_data_list = self.cursor.fetchall()

            for data in update_data_list:
                user_id = data[0]
                gift_from = data[4]

                search_query = (f'SELECT good_gift, bad_gift '
                                f'FROM secret_santa_{self.current_year} '
                                f'WHERE nickname = "{gift_from}"')
                self.cursor.execute(search_query)
                search_opponent = self.cursor.fetchall()

                for opponent in search_opponent:
                    if opponent[0] != '':
                        good_gift = f'он хотел бы получить _{opponent[0].lower()}_'
                    else:
                        good_gift = 'пожелания по подарку отсутствуют, выбор сделайте самостоятельно'

                    if opponent[1] != '':
                        bad_gift = f'А нежелательным подарком можно считать что-то из этого: _{opponent[1].lower()}_'
                    else:
                        bad_gift = 'Ограничений по нежелательным подаркам нет'

                    text_message = negative_result
                    if gift_from is not None:
                        text_message = (f'{positive_result}\n'
                                        f'Итак, его зовут *{gift_from}*, {good_gift}. {bad_gift}.\n'
                                        f'Все данные у вас есть. До Нового года ещё достаточно времени. '
                                        f'Удачи с выбором!')

                    # Secret.bot.send_photo(chat_id=Secret.list_admins.get('Никита'),
                    #                       photo=link_picture,
                    #                       caption=text_message,
                    #                       parse_mode="Markdown")
                    Secret.bot.send_photo(chat_id=user_id,
                                          photo=link_picture,
                                          caption=text_message,
                                          parse_mode="Markdown")
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def update_data_secret_santa(self, user_id, good_gift, bad_gift):
        update_query = (f'UPDATE secret_santa_{self.current_year} '
                        f'SET good_gift = "{good_gift}", bad_gift = "{bad_gift}" '
                        f'WHERE user_id = "{user_id}"')
        self.cursor.execute(update_query)
        self.sqlite_connection.commit()

    def check_user_in_table_secret_santa(self, user_id):
        """Проверка пользователя на наличие в таблице"""
        create_table = (f'CREATE TABLE IF NOT EXISTS secret_santa_{self.current_year}'
                        f'(Id INTEGER PRIMARY KEY AUTOINCREMENT,'
                        f'user_id INTEGER NOT NULL,'
                        f'user_name TEXT,'
                        f'nickname TEXT UNIQUE,'
                        f'good_gift TEXT,'
                        f'bad_gift TEXT,'
                        f'gift_from TEXT UNIQUE,'
                        f'gift_delivered INTEGER DEFAULT "0",'
                        f'gift_received INTEGER DEFAULT "0")')
        self.cursor.execute(create_table)
        self.sqlite_connection.commit()

        select_query = (f'SELECT user_id '
                        f'FROM secret_santa_{self.current_year} '
                        f'WHERE user_id = "{user_id}"')
        self.cursor.execute(select_query)
        user_id_in_table = self.cursor.fetchone()

        # print(user_id_in_table)

        if user_id_in_table is not None:
            return True
        else:
            return False

    def update_data_in_out(self, last_checkpoint):
        """Обновляет данные в таблице {IN_OUT}, устанавливает в колонке {Status} значение {last_checkpoint}"""

        try:
            sqlite_update_query = (f'UPDATE IN_OUT '
                                   f'SET Status = "{last_checkpoint}"')
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def checking_for_availability_in_cnn(self, user_id):
        """Возвращает True или False в зависимости от того, есть ли от пользователя предложения никнейма для
        Тайного Санты"""
        try:
            select_query = (f'SELECT id_user '
                            f'FROM creative_nick_NY '
                            f'WHERE id_user = "{user_id}"')
            self.cursor.execute(select_query)
            search_id = self.cursor.fetchone()
            if search_id is not None:
                return True
            else:
                return False
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            # logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def check_nickname_in_db(self, nickname):
        """Возвращает True или False в зависимости от того, есть ли никнейм в БД для Тайного Санты"""
        try:
            select_query = (f'SELECT id_user '
                            f'FROM creative_nick_NY '
                            f'WHERE proposal = "{nickname}"')
            self.cursor.execute(select_query)
            search_nickname = self.cursor.fetchone()
            if search_nickname is not None:
                return True
            else:
                return False
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def record_nickname_from_db(self, user_id, nickname):
        """Записывает новое имя для Тайного санты"""
        try:
            insert_query = f'INSERT INTO creative_nick_NY (id_user, proposal) ' \
                           f'VALUES ("{user_id}", "{nickname}")'
            self.cursor.execute(insert_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))

    def check_not_approve_nickname(self):
        """Возвращает имя которое не обработано админом"""
        try:
            select_query = (f'SELECT proposal '
                            f'FROM creative_nick_NY '
                            f'WHERE approval IS NULL')
            self.cursor.execute(select_query)
            search_nickname = self.cursor.fetchone()
            print(search_nickname)
            if search_nickname is not None:
                return search_nickname[0]
            else:
                return None
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def approve_nickname(self, nickname, status=None):
        """Устанавливает статус для присланных никнеймов. Возвращает user_id по найденному никнейму"""
        try:
            sqlite_update_query = (f'UPDATE creative_nick_NY '
                                   f'SET approval = "{status}" '
                                   f'WHERE proposal = "{nickname}"')
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()

            select_query = (f'SELECT id_user '
                            f'FROM creative_nick_NY '
                            f'WHERE proposal = "{nickname}"')
            self.cursor.execute(select_query)
            search_id_user = self.cursor.fetchone()
            if search_id_user is not None:
                return search_id_user[0]
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    def edit_message_lots(self, number_lot):
        try:
            select_query = (f'SELECT * '
                            f'FROM lots '
                            f'WHERE ID = "{number_lot}"')
            self.cursor.execute(select_query)
            data_from_db = self.cursor.fetchall()[0]

            name_lot = data_from_db[1]
            description_lot = data_from_db[2]
            id_photo = data_from_db[3]
            booked = data_from_db[4]
            booked_by_whom = data_from_db[5]
            booking_date = data_from_db[6]
            on_the_hands = data_from_db[7]
            who_took_it = data_from_db[8]
            date_of_issue = data_from_db[9]
            ids_message = eval(data_from_db[10])
            confirm = data_from_db[11]
            date_of_public = data_from_db[12]
            status = data_from_db[13]

            if booking_date != '':
                booking_date = datetime.datetime.strptime(booking_date, '%Y-%m-%d %H:%M:%S.%f')
                date_of_cancel = booking_date + datetime.timedelta(days=1)
                date_of_cancel_format = date_of_cancel.strftime("%d.%m.%Y %H:%M:%S")

            print(data_from_db)

            print(f'name_lot = {name_lot}')  # Название лота
            print(f'description_lot = {description_lot}')  # Описание лота
            print(f'id_photo = {id_photo}')  # ID фото
            print(f'booked = {booked}')  # Статус резерва (yes/no)
            print(f'booked_by_whom = {booked_by_whom}')  # Кем зарезервирован
            print(f'booking_date = {booking_date}')  # Дата брони
            print(f'on_the_hands = {on_the_hands}')  # Лот на руках? (yes/no)
            print(f'who_took_it = {who_took_it}')  # У кого на руках лот
            print(f'date_of_issue = {date_of_issue}')  # Дата выдачи лота на руки
            print(f'ids_message = {ids_message}')  # Словарь с id.user: id.message
            print(f'confirm = {confirm}')  # Подтверждение выдачи (yes/no)
            print(f'date_of_public = {date_of_public}')  # Дата публикации лота
            print(f'status = {status}')  # Статус активности лота (active/cancel)

            def edit_message(id_user, id_message, text=None, my_keyboard=None):
                if text is None:
                    description = (f'Лот №{number_lot}\n\n'
                                   f'Название: {name_lot}\n\n'
                                   f'Описание: {description_lot}\n\n')
                else:
                    description = (f'Лот №{number_lot}\n\n'
                                   f'Название: {name_lot}\n\n'
                                   f'Описание: {description_lot}\n\n'
                                   f'#####\n'
                                   f'{text}\n'
                                   f'#####')

                if my_keyboard is None:
                    Secret.bot.edit_message_caption(chat_id=id_user,
                                                    message_id=id_message,
                                                    caption=description)
                else:
                    Secret.bot.edit_message_caption(chat_id=id_user,
                                                    message_id=id_message,
                                                    caption=description,
                                                    reply_markup=my_keyboard)

            for user_id, message_id in ids_message.items():
                if status == 'cancel':  # Если лот аннулирован
                    date_today = datetime.datetime.now()
                    date_today_day = date_today.date()
                    date_today_format = date_today_day.strftime('%d.%m.%Y')

                    addition = f'Пост аннулирован {date_today_format} из-за срока давности\n'

                    edit_message(id_user=user_id, id_message=message_id, text=addition)
                elif status == 'active':  # Если лот активен
                    date_format = datetime.datetime.strptime(date_of_public, '%Y-%m-%d').date()
                    today = datetime.datetime.now().date()

                    dif_day = today - date_format
                    dif_day = dif_day.days
                    if dif_day > 30:  # Если лот активен более месяца
                        update_query = (f'UPDATE lots '
                                        f'SET status = "cancel" '
                                        f'WHERE ID = "{number_lot}"')
                        self.cursor.execute(update_query)
                        self.sqlite_connection.commit()
                    if confirm == 'yes':  # Если выдача лота подтверждена
                        if user_id == booked_by_whom:
                            addition = ('Выдача лота подтверждена.\n'
                                        'Поздравляем с приобретением!')

                            edit_message(id_user=user_id, id_message=message_id, text=addition)
                        else:
                            addition = 'Лот забрали. Он более недоступен'

                            edit_message(id_user=user_id, id_message=message_id, text=addition)
                    elif confirm == 'no':  # Если выдача лота не подтверждена
                        if on_the_hands == 'yes':  # Если пользователь указал что лот у него на руках
                            if user_id == booked_by_whom:
                                if self.check_for_admin(user_id) is True:  # Если пользователь админ
                                    str_dict_confirm = str({'confirm': number_lot})
                                    str_dict_refute = str({'refute': number_lot})

                                    keyboard = telebot.types.InlineKeyboardMarkup()
                                    button = telebot.types.InlineKeyboardButton(text='Подтвердить выдачу',
                                                                                callback_data=str_dict_confirm)
                                    button_2 = telebot.types.InlineKeyboardButton(text='Лот не выдан',
                                                                                  callback_data=str_dict_refute)
                                    keyboard.add(button, button_2)
                                    addition = 'Забрал лот?'
                                    edit_message(id_user=user_id, id_message=message_id, text=addition,
                                                 my_keyboard=keyboard)
                                else:
                                    addition = ('Вы указали, что забрали этот лот! Если выдача не подтвердится, '
                                                'статус сменится на "Этот лот забронирован вами".\n'
                                                'При получении лота покажите это сообщение, оно '
                                                'подтверждает, что он ЗАБРОНИРОВАН ВАМИ, а не '
                                                'кем-то другим.\n'
                                                'ВАЖНО!\n'
                                                'После того как лот окажется у вас на руках, обязательно подтвердите '
                                                'получение нажав кнопку "Лот уже у меня"!')

                                    edit_message(id_user=user_id, id_message=message_id, text=addition)
                            elif user_id != booked_by_whom:
                                if self.check_for_admin(user_id) is True:  # Если пользователь админ
                                    str_dict_confirm = str({'confirm': number_lot})
                                    str_dict_refute = str({'refute': number_lot})

                                    keyboard = telebot.types.InlineKeyboardMarkup()
                                    button = telebot.types.InlineKeyboardButton(text='Подтвердить выдачу',
                                                                                callback_data=str_dict_confirm)
                                    button_2 = telebot.types.InlineKeyboardButton(text='Лот не выдан',
                                                                                  callback_data=str_dict_refute)
                                    keyboard.add(button, button_2)
                                    addition = 'Подтвердить выдачу лота?'
                                    edit_message(id_user=user_id, id_message=message_id, text=addition,
                                                 my_keyboard=keyboard)
                                else:
                                    addition = ('Ожидает подтверждения выдачи. Если выдача не подтвердится, лот снова '
                                                'станет доступен. Следите за обновлениями!')

                                    edit_message(id_user=user_id, id_message=message_id, text=addition)
                        elif on_the_hands == 'no':
                            if booked == 'yes':  # Если пользователь забронировал лот
                                # Если получатель сообщения тот же человек, что забронировал лот
                                if user_id == booked_by_whom:
                                    str_dict_cancel = str({'cancel': number_lot})
                                    str_dict_sold = str({'sold': number_lot})

                                    keyboard = telebot.types.InlineKeyboardMarkup()
                                    button = telebot.types.InlineKeyboardButton(text='Отменить бронь',
                                                                                callback_data=str_dict_cancel)
                                    button_2 = telebot.types.InlineKeyboardButton(text='Лот уже у меня',
                                                                                  callback_data=str_dict_sold)
                                    keyboard.add(button, button_2)

                                    addition = (f'Этот лот забронирован вами до {date_of_cancel_format}. '
                                                f'Если забрать не успеваете, бронь аннулируется!')

                                    edit_message(id_user=user_id, id_message=message_id, text=addition,
                                                 my_keyboard=keyboard)
                                elif user_id != booked_by_whom:
                                    if self.check_for_admin(user_id) is True:  # Если пользователь админ
                                        select_query = (f'SELECT user_first_name, user_last_name '
                                                        f'FROM users '
                                                        f'WHERE user_id = "{booked_by_whom}"')
                                        self.cursor.execute(select_query)
                                        data_of_user = self.cursor.fetchone()  # Получаем данные о пользователе
                                        temp_list = []
                                        for elem in data_of_user:
                                            if elem is not None:
                                                temp_list.append(elem)

                                        full_name_user = ' '.join(temp_list)

                                        addition = (f'Лот зарезервирован пользователем <{full_name_user}>. '
                                                    f'Бронирование недоступно. '
                                                    f'Если до {date_of_cancel_format} его не заберут, '
                                                    f'бронь аннулируется и вы сможете отложить его для себя.')
                                        edit_message(id_user=user_id, id_message=message_id, text=addition)
                                    else:
                                        addition = (f'Лот зарезервирован. Бронирование недоступно. '
                                                    f'Если до {date_of_cancel_format} его не заберут, '
                                                    f'бронь аннулируется и вы сможете отложить его для себя.')
                                        edit_message(id_user=user_id, id_message=message_id, text=addition)
                            elif booked == 'no':
                                str_dict_lot = str({'lot': number_lot})
                                keyboard = telebot.types.InlineKeyboardMarkup()
                                button = telebot.types.InlineKeyboardButton(text='Забронировать лот',
                                                                            callback_data=str_dict_lot)
                                keyboard.add(button)
                                edit_message(id_user=user_id, id_message=message_id, my_keyboard=keyboard)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            logging_event(Secret.way_to_log_telegram_bot, 'error', str(error))
            pass
        except Secret.telebot.apihelper.ApiTelegramException as error:
            response = error.result_json
            print(response)
            status = response.get('ok')
            if status is not True:
                text_error = f'Не удаётся обновить лот у пользователя {user_id}.'
                print('status not True')
                description = response.get('description')
                reason = description
                if error.error_code == 400:
                    if description == ('Bad Request: message is not modified: specified new message content '
                                       'and reply markup are exactly the same as a current content and reply '
                                       'markup of the message'):
                        reason = 'Сообщение не изменено т.к. нет изменений.'
                        pass
                    elif description == 'Bad Request: message to edit not found':
                        reason = 'Сообщения с таким id не существует.'
                    elif description == 'Bad Request: chat not found':
                        reason = f'Боту неизвестен чат с пользователем {user_id}'
                    elif description == 'Forbidden: bot was blocked by the user':
                        reason = f'Пользователь {user_id} заблокировал бота'

                answer_message = f'{text_error}\n{reason}'
                print(answer_message)


class Decorators:
    """

    """

    def __init__(self, message):
        self.message = message
        self.time_now = lambda x: time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(x))  # Дата в читабельном виде
        self.check_admin = SQL().check_for_admin(self.message.from_user.id)  # Проверка является ли пользователь админом

    def _full_name_user(self, func):
        """
        Печатает в консоль имя пользователя: Администратор/Пользователь + Имя + ID
        :param func:
        :return: {time_now}\n{Администратор/Пользователь} {Имя} {ID} отправил команду:\n{message.text}
        """

        if self.check_admin is True:
            status_user = 'Администратор'
        else:
            status_user = 'Пользователь'
        name_user = f'{self.message.from_user.first_name} (ID: {self.message.from_user.id})'  # Получаем имя и id
        pattern = f'{self.time_now(self.message.date)}\n' \
                  f'{status_user} {name_user} отправил команду:\n' \
                  f'{self.message.text}'  # Итог дата, \n, статус и ID пользователя
        print(f'Сработал декоратор {Decorators._full_name_user.__name__}\n{pattern}')
        return func


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
