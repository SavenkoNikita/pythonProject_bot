# import time
#
# import Data
# import SQLite
# from Data import bot
#
#
# @bot.message_handler(content_types=['text'])
# def other_functions(message):
#     bot.send_message(message.chat.id, message.text)
#     bot.send_message(message.from_user.id, SQLite.Message.user_data(message).id)
#     SQLite.Message.db_table_val(message)
#
#
# if __name__ == '__main__':
#     while True:
#         try:
#             bot.polling(none_stop=True)
#         except Exception as e:
#             time.sleep(3)
#             bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
#             print(str(e))
