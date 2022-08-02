import datetime
import random
import time
import traceback

import schedule

import Data
import Other_functions.Functions
import Test_2
from Data import bot
from Other_functions import Functions, Working_with_notifications
from Other_functions.File_processing import Working_with_a_file
from Other_functions.Functions import logging_scheduler
from Other_functions.Tracking_sensor import TrackingSensor


def random_time():
    """Возвращает строку случайного времени от 7:00 до 7:59"""
    time_str = '7:{:02d}'.format(random.randint(0, 59))
    return time_str


def check_dej():
    text_log_info = f'Сработала функция check_dej()'
    logging_scheduler('info', text_log_info)
    Working_with_a_file('Дежурный').check_dej_tomorrow()


def check_sensors():
    # text_log = f'Сработала функция check_sensors()'
    # logging_scheduler('info', text_log)
    Working_with_notifications.Notification().update_mess('observers_for_faulty_sensors',
                                                          TrackingSensor().check_all())
    Working_with_notifications.Notification().update_mess('tracking_sensor_defroster',
                                                          TrackingSensor().check_defroster())
    Test_2.test()


def check_event(sheet_name):
    text_log_info = f'Сработала функция check_event()'
    logging_scheduler('info', text_log_info)
    Working_with_a_file(sheet_name).check_event_today()


def top_statistic():
    Other_functions.Functions.SQL().reset_count_request()
    text_top_user = Other_functions.Functions.SQL().top_chart()
    bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_top_user)


# Проверяет и уведомляет есть ли завтра дежурный
schedule.every().day.at('15:00').do(check_dej)

# Если инвент вот-вот начнётся, придёт уведомление
schedule.every().day.at('07:00').do(check_event, 'Инвентаризация')

# Присылает случайное имя кто идёт в цех
schedule.every().day.at('07:01').do(Functions.random_name)

# Проверяет есть ли сегодня уведомления для подписчиков и отправляет их
schedule.every().day.at('08:00').do(check_event, 'Уведомления для подписчиков')

# Проверяет есть ли сегодня уведомления для всех и отправляет их
schedule.every().day.at('08:01').do(check_event, 'Уведомления для всех')

# Проверяет есть ли сегодня уведомления для админов и отправляет их
schedule.every().day.at('08:02').do(check_event, 'Уведомления для админов')

# Обновляет информацию о датчиках
schedule.every(1).minutes.do(check_sensors)
# schedule.every(10).seconds.do(Working_with_notifications.Notification().update_mess('observers_for_faulty_sensors',
#                                                                                     TrackingSensor().check_all))
# schedule.every(10).seconds.do(Working_with_notifications.Notification().update_mess('tracking_sensor_defroster',
#                                                                                     TrackingSensor().check_defroster))

schedule.every().day.at('00:01').do(top_statistic)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        text_error = traceback.format_exc()
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Scheduler: сработало исключение.')
        # print(text_error)
        # Other_functions.logging_event('error', text_error)
        print(datetime.datetime.now())
        print(e)
        text_log = f'Scheduler: возникло исключение <{e}>.\nПодробности: {text_error}'
        logging_scheduler('debug', text_log)
