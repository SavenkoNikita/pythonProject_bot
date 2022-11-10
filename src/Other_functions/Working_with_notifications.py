import sqlite3
import time

import telebot

import Data
# from Other_functions.Functions import logging_event, pack_in_callback_data, SQL
from src.Other_functions import Functions


def repeat_for_list(data_list, user_id, count=1):
    f"""Присылает {count} элементов из списка {data_list} пользователю {user_id}. Если не указать {count},
    пришлёт первый элемент из списка."""

    temporary_list = []
    for elem in range(0, count):
        Data.bot.send_message(user_id, data_list[elem])
        temporary_list.append(data_list[elem])

    print('Бот ответил:')
    for i in temporary_list:
        print(i)


class Notification:
    """Методы уведомлений"""

    def __init__(self):
        self.sqlite_connection = sqlite3.connect(Data.way_sql)
        self.cursor = self.sqlite_connection.cursor()

    def send_a_notification_to_all_users(self, text_message):
        f"""Принимает {text_message} и отправляет его всем пользователям находящимся в БД."""

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
                username = Functions.SQL().get_user_info(all_user_sql[i])
                try:
                    print(username)
                    Data.bot.send_message(all_user_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Data.telebot.apihelper.ApiTelegramException:
                    text_error = 'Пользователь <' + username + '> заблокировал бота!'
                    print(text_error)
                    Functions.logging_event('error', str(text_error))
                    Functions.SQL().log_out(all_user_sql[i])
                i += 1
        except sqlite3.Error as error:
            print('Ошибка при работе с SQLite', error)
            Functions.logging_event('error', error)
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print('Соединение с SQLite закрыто')

    def notification_for(self, text_message, column, column_meaning):
        f"""Уведомления для юзеров с указанными параметрами. Принимает {text_message}, название столбца в БД {column}, 
        и искомое значение этой колонки {column_meaning}. Например - я хочу уведомить подписчиков о событии, 
        это будет выглядеть так: notification_for('Сообщение, которое хочу передать', 'notification', 'yes')."""

        try:
            self.cursor.execute(f'SELECT * FROM users WHERE {column}= ?', [column_meaning])
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
                username = Functions.SQL().get_user_info(all_id_sql[i])
                try:
                    print(username)
                    Data.bot.send_message(all_id_sql[i], text=text_message)
                    # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
                except Data.telebot.apihelper.ApiTelegramException:
                    text_error = f'Пользователь <{username}> заблокировал бота!'
                    print(text_error)
                    Functions.logging_event('error', str(text_error))
                    Functions.SQL().log_out(all_id_sql[i])
                i += 1
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event('error', error)
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def send_notification_to_subscribers(self, text_message):
        """Отправляет уведомление подписчикам"""

        self.notification_for(text_message, 'notification', 'yes')

    def send_notification_to_administrators(self, text_message):
        """Отправляет уведомление администраторам"""

        self.notification_for(text_message, 'status', 'admin')

    def send_sticker_for(self, column, column_meaning, user_sticker):
        """Уведомления для юзеров с указанными параметрами"""
        try:
            self.cursor.execute(f'SELECT * FROM users WHERE {column}= ?', [column_meaning])
            records = self.cursor.fetchall()
            # print('Список ID:\n')
            all_id_sql = []
            for row in records:
                all_id_sql.append(row[1])
            self.cursor.close()
            # print(all_id_sql)
            i = 0
            print('Стикер отправлен следующим пользователям:\n')
            # user_sticker = File_processing('Дежурный').sticker_next_dej()
            while i < len(all_id_sql):
                username = Functions.SQL().get_user_info(all_id_sql[i])
                try:
                    print(username)
                    # user_sticker = SQL().get_user_sticker(get_key(user_first_name))
                    Data.bot.send_sticker(all_id_sql[i], user_sticker)
                    # Data.bot.send_sticker(Data.list_admins.get('Никита'), user_sticker)
                except Data.telebot.apihelper.ApiTelegramException:
                    print(f'Пользователь <{username}> заблокировал бота!')
                    Functions.SQL().log_out(username)
                except Exception as e:
                    time.sleep(3)
                    Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=f'Бот выдал ошибку: {str(e)}')
                    print(str(e))
                    Functions.logging_event('error', str(e))
                i += 1
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event('error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def send_sticker_to_subscribers(self, sticker):
        """Отправка стикера дежурного подписчикам"""

        self.send_sticker_for('notification', 'yes', sticker)

    def send_sticker_to_administrators(self, sticker):
        """Отправка стикера дежурного администраторам"""

        self.send_sticker_for('status', 'admin', sticker)

    def update_mess(self, name_table_DB, func):
        """Обновляет сообщение у пользователей."""

        try:
            text_message = func
            data_list = Functions.SQL().get_dict(name_table_DB)
            if len(data_list) != 0:
                for elem in data_list:
                    user_id = elem[0]
                    message_id = elem[1]
                    Data.bot.edit_message_text(text=text_message,
                                               chat_id=user_id,
                                               message_id=message_id,
                                               parse_mode='Markdown')
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()

    def notification_for_subs_lots(self, name_lot, photo_id, description, name_key_callback_data='lot'):
        f"""Отправляет уведомление всем пользователям подписчикам барахолки"""

        try:
            self.cursor.execute('SELECT user_id FROM users WHERE sub_bar = "yes"')
            records = self.cursor.fetchall()
            all_id_sql = []
            for row in records:
                all_id_sql.append(row)

            ids_message = {}
            id_callback_data = Notification().get_last_record_lots()

            for ids in all_id_sql:
                try:
                    ids = ids[0]

                    # Упаковывает ключ и значение в str(словарь)
                    callback_data = Functions.pack_in_callback_data(name_key_callback_data, id_callback_data)

                    keyboard = telebot.types.InlineKeyboardMarkup()
                    button = telebot.types.InlineKeyboardButton(text='Забронировать лот', callback_data=callback_data)
                    keyboard.add(button)

                    message_id = Data.bot.send_photo(chat_id=ids,
                                                     caption=f'Лот №{id_callback_data}\n\n' \
                                                             f'Название: {name_lot}\n\n' \
                                                             f'Описание: {description}\n\n',
                                                     photo=photo_id,
                                                     reply_markup=keyboard).message_id
                    Data.bot.pin_chat_message(chat_id=ids,
                                              message_id=message_id)  # Закрепляет сообщение у пользователя

                    ids_message[ids] = message_id
                except telebot.apihelper.ApiException as error:
                    Functions.SQL().change_status_bar(ids)
                    text = f'При рассылке лота пользователю {ids} возникла ошибка: \n{error}\n' \
                           f'Статус подписки, этого пользователя на барахолку, изменён на "no"'
                    message_id = Data.bot.send_message(chat_id=Data.list_admins.get('Никита'),
                                                       text=text).message_id
                    Data.bot.pin_chat_message(chat_id=Data.list_admins.get('Никита'),
                                              message_id=message_id)
                    pass

            # print(ids_message)

            # self.cursor.execute('SELECT ID FROM lots ORDER BY ID DESC LIMIT 1')
            # record_id = self.cursor.fetchone()[0]
            record_id = self.get_last_record_lots()

            self.cursor.execute(f'UPDATE lots SET ids_message = "{ids_message}" WHERE ID = {record_id}')
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
        finally:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def get_last_record_lots(self):
        try:
            self.cursor.execute('SELECT ID FROM lots ORDER BY ID DESC LIMIT 1')
            record_id = self.cursor.fetchone()[0]
            return record_id
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def notification_for_sub_baraholka(self, text_message):
        """Инструмент для отправки текстового сообщения подписчикам барахолки"""

        try:
            self.cursor.execute('SELECT user_id FROM users WHERE sub_bar = "yes"')
            records = self.cursor.fetchall()
            for ids in records:
                ids = ids[0]
                Data.bot.send_message(chat_id=ids, text=text_message)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event(Data.way_to_log_telegram_bot, 'error', str(error))

    def notif_test_message(self, text_message, id_photo):
        """"""
        try:
            self.cursor.execute('SELECT user_id FROM users WHERE sub_bar = "yes"')
            records = self.cursor.fetchall()
            for ids in records:
                ids = ids[0]
                Data.bot.send_photo(chat_id=ids, text=text_message)
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
            Functions.logging_event(Data.way_to_log_telegram_bot, 'error', str(error))
