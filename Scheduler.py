import time
import traceback

import schedule

import Data
import Functions
import Tracking_sensor
from Functions import random_name


def check_sensors():
    Functions.Notification().update_mess('observers_for_faulty_sensors',
                                         Tracking_sensor.TrackingSensor().check_all())
    Functions.Notification().update_mess('tracking_sensor_defroster',
                                         Tracking_sensor.TrackingSensor().check_defroster())


def check_event(sheet_name):
    Functions.File_processing(sheet_name).check_event_today()


# Проверяет и уведомляет есть ли завтра дежурный
schedule.every().day.at('15:00').do(Functions.File_processing('Дежурный').check_dej_tomorrow)

# Если инвент вот-вот начнётся, придёт уведомление
schedule.every().day.at('07:00').do(check_event('Инвентаризация'))

# Проверяет есть ли сегодня уведомления для подписчиков и отправляет их
schedule.every().day.at('08:00').do(check_event('Уведомления для подписчиков'))

# Проверяет есть ли сегодня уведомления для всех и отправляет их
schedule.every().day.at('08:01').do(check_event('Уведомления для всех'))

# Проверяет есть ли сегодня уведомления для админов и отправляет их
schedule.every().day.at('08:02').do(check_event('Уведомления для админов'))

# Присылает случайное имя кто идёт в цех
schedule.every().day.at('08:03').do(random_name)

# Обновляет информацию о датчиках
schedule.every(1).minutes.do(check_sensors)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        # text_error = traceback.format_exc()
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_error)
        # print(text_error)
        # Functions.logging_event('error', text_error)
        print(e)
