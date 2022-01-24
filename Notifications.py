# import sqlite3
# import time
#
# import Classes
# import Data
# import Other_function
# import SQLite


# Функция для уведомления всех пользователей находящихся в БД
# def notification_all_reg(text_message):
#     sqlite_connection = sqlite3.connect(Data.way_sql)
#     try:
#         cursor = sqlite_connection.cursor()
#
#         sqlite_select_query = 'SELECT * from users where user_id'
#         cursor.execute(sqlite_select_query)
#         records = cursor.fetchall()
#         all_user_sql = []
#         for row in records:
#             all_user_sql.append(row[1])
#         cursor.close()
#         i = 0
#         print('Уведомление отправлено следующим пользователям:\n')
#         while i < len(all_user_sql):
#             username = Classes.SQL(message).get_user_info(all_user_sql[i])
#             try:
#                 print(username)
#                 Data.bot.send_message(all_user_sql[i], text=text_message)
#                 # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
#             except Data.telebot.apihelper.ApiTelegramException:
#                 text_error = 'Пользователь <' + username + '> заблокировал бота!'
#                 print(text_error)
#                 Other_function.logging_event('error', str(text_error))
#                 Classes.SQL(message).log_out(all_user_sql[i])
#             i += 1
#     except sqlite3.Error as error:
#         print('Ошибка при работе с SQLite', error)
#         Other_function.logging_event('error', error)
#     finally:
#         if sqlite_connection:
#             sqlite_connection.close()
#             print('Соединение с SQLite закрыто')


# # Уведомления для юзеров с указанными параметрами
# def notification_for(text_message, column, column_meaning):
#     sqlite_connection = sqlite3.connect(Data.way_sql)
#     try:
#         cursor = sqlite_connection.cursor()
#         # print('Подключен к SQLite')
#
#         sqlite_select_query = 'SELECT * FROM users WHERE ' + column + ' = ?'
#         cursor.execute(sqlite_select_query, [column_meaning])
#         records = cursor.fetchall()
#         # print('Список ID:\n')
#         all_id_sql = []
#         for row in records:
#             all_id_sql.append(row[1])
#         cursor.close()
#         # print(all_id_sql)
#         i = 0
#         print('Уведомление отправлено следующим пользователям:\n')
#         while i < len(all_id_sql):
#             username = SQLite.get_user_info(all_id_sql[i])
#             try:
#                 print(username)
#                 Data.bot.send_message(all_id_sql[i], text=text_message)
#                 # Data.bot.send_message(Data.list_admins.get('Никита'), text=text_message)
#             except Data.telebot.apihelper.ApiTelegramException:
#                 text_error = 'Пользователь <' + username + '> заблокировал бота!'
#                 print(text_error)
#                 Other_function.logging_event('error', str(text_error))
#                 SQLite.log_out(all_id_sql[i])
#             i += 1
#     except sqlite3.Error as error:
#         print("Ошибка при работе с SQLite", error)
#         Other_function.logging_event('error', error)
#     finally:
#         if sqlite_connection:
#             sqlite_connection.close()
#             print("Соединение с SQLite закрыто")


# Уведомления для юзеров с указанными параметрами
# def send_sticker_for(user_first_name, column, column_meaning):
#     sqlite_connection = sqlite3.connect(Data.way_sql)
#     try:
#         cursor = sqlite_connection.cursor()
#
#         sqlite_select_query = 'SELECT * FROM users WHERE ' + column + ' = ?'
#         cursor.execute(sqlite_select_query, [column_meaning])
#         records = cursor.fetchall()
#         # print('Список ID:\n')
#         all_id_sql = []
#         for row in records:
#             all_id_sql.append(row[1])
#         cursor.close()
#         # print(all_id_sql)
#         i = 0
#         print('Стикер отправлен следующим пользователям:\n')
#         while i < len(all_id_sql):
#             username = SQLite.get_user_info(all_id_sql[i])
#             try:
#                 print(username)
#                 user_sticker = SQLite.get_user_sticker(Other_function.get_key(Data.user_data, user_first_name))
#                 Data.bot.send_sticker(all_id_sql[i], user_sticker)
#                 # Data.bot.send_sticker(Data.list_admins.get('Никита'), user_sticker)
#             except Data.telebot.apihelper.ApiTelegramException:
#                 print('Пользователь <' + username + '> заблокировал бота!')
#                 SQLite.log_out(username)
#             except Exception as e:
#                 time.sleep(3)
#                 Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
#                 print(str(e))
#                 Other_function.logging_event('error', str(e))
#             i += 1
#     except sqlite3.Error as error:
#         print("Ошибка при работе с SQLite", error)
#         Other_function.logging_event('error', str(error))
#     finally:
#         if sqlite_connection:
#             sqlite_connection.close()
#             print("Соединение с SQLite закрыто")
