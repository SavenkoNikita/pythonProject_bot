import random
import time
import datetime

import schedule

import Data
import Other_function


def sh_random_name():
    """Присылает уведомление кто сегодня закрывает сигналы"""
    if datetime.datetime.today().isoweekday() <= 5:
        list_name = ['Паша', 'Дима', 'Никита']
        random_name = random.choice(list_name)
        end_text = f'Случайным образом определено, что сигналы сегодня закрывает {random_name}'
        for i in list_name:
            Data.bot.send_message(chat_id=Data.list_admins.get(i), text=end_text)


def repeat_for_list():
    for i in Data.sheets_file:
        Other_function.File_processing(i).check_event_today()


time_dej = '15:00'
time_other = '08:00'

# Проверяет и уведомляет о дежурном
schedule.every().day.at(time_dej).do(Other_function.File_processing('Дежурный').check_event_today)
# Проверяет есть ли сегодня уведомления
schedule.every().day.at(time_other).do(repeat_for_list)
# Присылает случайное имя кто идёт в цех
schedule.every().day.at(time_other).do(sh_random_name)

while True:
    schedule.run_pending()
    time.sleep(1)
