import random
import time
import datetime
import traceback

import schedule

import Data
import Functions


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
        Functions.File_processing(i).check_event_today()


time_dej = '15:00'
# Проверяет и уведомляет есть ли завтра дежурный
schedule.every().day.at(time_dej).do(Functions.File_processing('Дежурный').check_dej_tomorrow)

time_other = '08:00'
# Проверяет есть ли сегодня уведомления
schedule.every().day.at(time_other).do(repeat_for_list)
# Присылает случайное имя кто идёт в цех
schedule.every().day.at(time_other).do(sh_random_name)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        time.sleep(3)
        text_message = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nScheduler был прерван вручную'
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_message)
        print(text_message)
        Functions.logging_event('error', text_message)
        break
    except Exception:
        text_error = traceback.format_exc()
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_error)
        print(text_error)
        Functions.logging_event('error', text_error)
        break
