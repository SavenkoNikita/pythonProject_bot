import datetime
import random
import time
import traceback

import requests
import schedule

import Data
# import Other_functions.Functions
import Test_2
import src.Other_functions.Functions
from Data import bot
from src.Other_functions import Working_with_notifications, Functions
from src.Other_functions.File_processing import Working_with_a_file
from src.Other_functions.Functions import logging_scheduler
from src.Other_functions.Tracking_sensor import TrackingSensor


def update_lots():
    src.Other_functions.Functions.SQL().schedule_updating_data_on_lots()


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
    src.Other_functions.Functions.SQL().get_list_faulty_sensors()


def check_bird():
    Test_2.test()


def check_event(sheet_name):
    text_log_info = f'Сработала функция check_event()'
    logging_scheduler('info', text_log_info)
    Working_with_a_file(sheet_name).check_event_today()


def top_statistic():
    text_top_user = Functions.SQL().top_chart()
    bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_top_user)


def update_the_reservation_status_of_lots():
    Functions.SQL().schedule_cancel_booking()
    Functions.SQL().schedule_cancel_lot()


def check_top_byers():
    if datetime.date.today().day == 1:  # Если сегодня 1-е число месяца
        top = Functions.SQL().create_string_top_byers_all_time()
        Working_with_notifications.Notification().send_notification_to_administrators(top)
        print(top)


def the_most_active_user():
    if datetime.date.today().day == 1:  # Если сегодня 1-е число месяца
        Working_with_notifications.Notification().notification_for_top_user()


# Проверяет и уведомляет есть ли завтра дежурный
schedule.every().day.at('15:00').do(check_dej)

# Если инвент вот-вот начнётся, придёт уведомление
schedule.every().day.at('07:00').do(check_event, 'Инвентаризация')

# Присылает случайное имя кто идёт в цех
# schedule.every().day.at('07:01').do(Functions.random_name)

# Присылает админам топ самых жадных барахольщиков
schedule.every().day.at('07:02').do(check_top_byers)

# Рассылает всем причастным, топ самых активных пользователей
schedule.every().day.at('07:03').do(the_most_active_user)

# Проверяет есть ли сегодня уведомления для подписчиков и отправляет их
schedule.every().day.at('08:00').do(check_event, 'Уведомления для подписчиков')

# Проверяет есть ли сегодня уведомления для всех и отправляет их
schedule.every().day.at('08:01').do(check_event, 'Уведомления для всех')

# Проверяет есть ли сегодня уведомления для админов и отправляет их
schedule.every().day.at('08:02').do(check_event, 'Уведомления для админов')

# Проверяет есть ли сегодня уведомления для подписчиков барахолки и отправляет их
schedule.every().day.at('08:03').do(check_event, 'Уведомления для барахолки')

# Обновляет информацию о датчиках
schedule.every(1).minutes.do(check_sensors)

# Обновить статус брони лотов
schedule.every(1).minutes.do(update_the_reservation_status_of_lots)

# Присылает топ чарт лидеров по кол-ву запросов к боту
schedule.every().day.at('00:01').do(top_statistic)

# Мониторинг пользователей
schedule.every(10).seconds.do(check_bird)

# schedule.every().day.at('00:01').do(update_lots)
# schedule.every(1).minutes.do(update_lots)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except requests.exceptions.ReadTimeout:
        time.sleep(3)
        text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nПревышено время ожидания запроса'
        # bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text)
        print(text)
    except requests.ConnectionError:
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nНет соединения с сервером')
        time.sleep(60)
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nПопытка соединения')
    except Exception as e:
        text_error = traceback.format_exc()
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Scheduler: сработало исключение.')
        # print(text_error)
        # Other_functions.logging_event('error', text_error)
        print(datetime.datetime.now())
        print(e)
        text_log = f'Scheduler: возникло исключение <{e}>.\nПодробности: {text_error}'
        logging_scheduler('debug', text_log)
