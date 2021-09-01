# import datetime
# import time
#
# import Data
# import SQLite
# import What_i_can_do
#
# bot = Data.bot
#
#
# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):
#     check_admin = What_i_can_do.check_admin(message.from_user.id)
#     now_date = datetime.datetime.now()
#     now_date = now_date.strftime("%d.%m.%Y %H:%M:%S")
#     full_name_user = message.from_user.first_name + ' (ID: ' + str(message.from_user.id) + ') '
#
#     if check_admin == 'yes':
#         status_user = 'Администратор '
#     else:
#         status_user = 'Пользователь '
#
#     pattern = now_date + '\n' + status_user + full_name_user
#     message_user = pattern + 'отправил команду ' + message.text
#     answer_bot = 'Бот ответил:\n'
#
#     if message.text == "/start":
#         print(message_user)
#         # Приветственное сообщение
#         Data.bot.send_message(message.from_user.id, 'Добро пожаловать ' + message.from_user.first_name)
#         print(answer_bot)
#         SQLite.welcome(message)
#     elif message.text == "/help":
#         print(message_user)
#         bot.send_message(message.from_user.id, What_i_can_do.can_help(message))
#         print(answer_bot + What_i_can_do.can_help(message) + '\n')
#     elif message.text in What_i_can_do.command_to_def:
#         print(message_user)
#         bot.send_message(message.from_user.id, What_i_can_do.command_to_def[message.text])
#         print(answer_bot + What_i_can_do.command_to_def[message.text] + '\n')
#     else:
#         print(pattern + 'написал: ' + '"' + message.text + '"')
#         i_can = "Чтобы узнать что я умею напиши /help."
#         bot.send_message(message.from_user.id, i_can)
#         print(answer_bot + i_can + '\n')
#
#
# if __name__ == '__main__':
#     while True:
#         try:
#             bot.polling(none_stop=True)
#         except Exception as e:
#             time.sleep(3)
#             bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
#             print(e)
