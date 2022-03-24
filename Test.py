# import Data
# import Other_function
#
# for i in Data.sheets_file:
#     print(i)
#     print(f'{Other_function.File_processing(i).read_file()}\n\n')
# import time
#
# import Data
# import Other_function
# import Tracking_sensor
# from Data import bot

# test_list = ['Тестовое сообщение',
#              'Тестовое сообщение2',
#              'Тестовое сообщение3'
#              ]
# for i in test_list:
#     bot.send_message(chat_id=Data.list_admins.get('Никита'), text=i)
#     time.sleep(5)
#     bot.delete_message(chat_id=Data.list_admins.get('Никита'), message_id=bot.send_message(chat_id=Data.list_admins.get('Никита'), text=i))

# bot.delete_message(chat_id=Data.list_admins.get('Никита'), message_id=1)
# list_id = [
#     Data.list_admins.get('Никита'),
#     368861606
# ]
#
# for id in list_id:
#     bot.send_poll(id, 'вопрос', options=['1', '2', '3'],)

# print(Other_function.File_processing('Уведомления для подписчиков').check_event_today())
# print(Other_function.File_processing('Дежурный').read_file())
# print(Other_function.File_processing('Дежурный').next_dej())
# import datetime

# import Functions
# import Other_function



# text_message = 0
# id_mes = bot.send_message(Data.list_admins.get('Никита'), text_message)
# bot.pin_chat_message(chat_id=Data.list_admins.get('Никита'), message_id=id_mes.message_id)
# while text_message < 10:
#     text_message += 1
#     bot.edit_message_text(text=text_message, chat_id=Data.list_admins.get('Никита'), message_id=id_mes.message_id)
#     time.sleep(5)

# my_dict = {'test': 1}
# print(my_dict)
# my_dict['test2'] = 2
# print(my_dict)

# print(Tracking_sensor.TrackingSensor().check_defroster())

# print(Other_function.File_processing('Уведомления для подписчиков').create_event('18.03.2022', 'test'))

# date = '18.03.2022'
# date_obj = datetime.datetime.strptime(date, '%d.%m.%Y')
# date_obj = date_obj.date().strftime('%d.%m.%Y')
# print(date_obj)

# Other_function.File_processing('Дежурный').check_dej_tomorrow()
# import Scheduler
#
# Scheduler.repeat_for_list()
import Functions

# data_list = Functions.File_processing('Уведомления для подписчиков').read_file()
#
# if data_list is not None:
#     for i in data_list:
#         if len(i) == 2:
#             print(f'Первая дата: {type(i[0])}({i[0]})\nТекст: {type(i[1])}({i[1]})\n')
#             print(i)
#             print(f'Кол-во значений: {len(i)}\n\n')
#         elif len(i) == 3:
#             print(f'Первая дата: {type(i[0])}({i[0]})\nВторая дата: {type(i[1])}({i[1]})\nТекст: {type(i[2])}({i[2]})\n')
#             print(i)
#             print(f'Кол-во значений: {len(i)}\n\n')

# Functions.File_processing('Уведомления для подписчиков').clear_old_data()

# if -13 <= -999.9:
#     print(True)
# else:
#     print(False)

print(Functions.File_processing('Дежурный').next_dej())
