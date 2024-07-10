import datetime
import inspect
import random
import time
import traceback

import requests
import schedule

# import Data
from Tests.Test_2 import test
from src.Body_bot import Secret
from src.Body_bot.Secret import bot, list_admins
from src.Other_functions.Functions import SQL, name_hero
from src.Other_functions.Working_with_notifications import Notification
from src.Other_functions.File_processing import Working_with_a_file
from src.Other_functions.Tracking_devices import TrackingSensor


def test_random_time():
    bot.send_message(chat_id=list_admins.get('Никита'),
                     text='Test random time\n'
                          '07:{:02d}.format(random.randint(0, 59))')


def top_statistic():
    text_top_user = SQL().top_chart()
    bot.send_message(chat_id=list_admins.get('Никита'),
                     text=text_top_user,
                     disable_notification=True)


def check_top_byers(silent=True):
    if datetime.date.today().day == 1:  # Если сегодня 1-е число месяца
        top = SQL().create_string_top_byers_all_time()
        Notification().send_notification_to_administrators(top, silent)
        print(top)


def the_most_active_user():
    if datetime.date.today().day == 1:  # Если сегодня 1-е число месяца
        Notification().notification_for_top_user()


def start_the_draw_santa():
    current_year = datetime.datetime.now().year
    date_start = datetime.datetime.strptime(f'{current_year}-12-01', '%Y-%m-%d').date()

    if datetime.date.today() == date_start:  # Если сегодня 1-е декабря
        SQL().selecting_opponent_secret_santa()


###
"""Test rand time job"""


def schedule_next_run():
    def create_random_time(summary=None):
        hour = '{:02d}'.format(random.randint(00, 23))

        if summary == 'first':
            hour = '07'
        elif summary == 'second':
            hour = '08'
        elif summary == 'daily':
            hour = '{:02d}'.format(random.randint(14, 17))
        else:
            hour = hour

        minutes = '{:02d}'.format(random.randint(0, 59))
        time_str = f'{hour}:{minutes}'
        # print(time_str)
        return time_str

    print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nОбновление расписания заданий\n')

    schedule.clear('first summary')  # Clear old time
    schedule.clear('second summary')
    schedule.clear('daily summary')

    # schedule.every().day.at(create_random_time(summary='first')). \
    #     do(test_random_time). \
    #     tag('first summary')

    # Если инвент вот-вот начнётся, придёт уведомление
    schedule.every().day.at(create_random_time(summary='first')). \
        do(Working_with_a_file('Инвентаризация').check_event_today, silent=True). \
        tag('first summary')

    # Присылает имя того кто идёт в цех
    schedule.every().day.at(create_random_time(summary='second')). \
        do(name_hero). \
        tag('second summary')

    # Проверяет есть ли сегодня уведомления для подписчиков и отправляет их
    schedule.every().day.at(create_random_time(summary='second')). \
        do(Working_with_a_file('Уведомления для подписчиков').check_event_today). \
        tag('second summary')

    # Проверяет есть ли сегодня уведомления для всех и отправляет их
    schedule.every().day.at(create_random_time(summary='second')). \
        do(Working_with_a_file('Уведомления для всех').check_event_today). \
        tag('second summary')

    # Проверяет есть ли сегодня уведомления для админов и отправляет их
    schedule.every().day.at(create_random_time(summary='second')). \
        do(Working_with_a_file('Уведомления для админов').check_event_today). \
        tag('second summary')

    # Проверяет есть ли сегодня уведомления для подписчиков барахолки и отправляет их
    schedule.every().day.at(create_random_time(summary='second')). \
        do(Working_with_a_file('Уведомления для барахолки').check_event_today). \
        tag('second summary')

    # Присылает админам топ самых жадных барахольщиков
    schedule.every().day.at(create_random_time(summary='daily')). \
        do(check_top_byers, silent=True).tag('daily summary')

    # Рассылает всем причастным, топ самых активных пользователей
    schedule.every().day.at(create_random_time(summary='daily')). \
        do(the_most_active_user). \
        tag('daily summary')


def update_data_sensors():
    all_sensors = TrackingSensor().check_all()
    defrosters = TrackingSensor().check_defroster()
    Notification().update_mess(name_table_DB='observers_for_faulty_sensors',
                               text_message=all_sensors,
                               name_table_up_stat='users',
                               set_name_column='observer_all_sensor',
                               set_value_column='no')

    Notification().update_mess(name_table_DB='tracking_sensor_defroster',
                               text_message=defrosters,
                               name_table_up_stat='users',
                               set_name_column='def',
                               set_value_column='no')


# Проверяет и уведомляет есть ли завтра дежурный
schedule.every().day.at('15:00').do(Working_with_a_file('Дежурный').check_dej_tomorrow)

# Обновляет информацию о датчиках
schedule.every(1).minutes.do(update_data_sensors)

# Добавляет в Yougile задачу если есть неисправный датчик
schedule.every(1).minutes.do(SQL().get_list_faulty_sensors)

# Обновить статус брони лотов
schedule.every(1).minutes.do(SQL().schedule_cancel_booking)
schedule.every(1).minutes.do(SQL().schedule_cancel_lot)

#  Create random schedule with jobs
schedule.every().day.at('00:00').do(schedule_next_run)
schedule_next_run()
# schedule.every(5).seconds.do(job)

# Присылает топ чарт лидеров по кол-ву запросов к боту
schedule.every().day.at('00:00').do(top_statistic)

# Мониторинг пользователей
schedule.every(10).seconds.do(test)

# Запустить жеребьёвку участников Тайного Санты
schedule.every(1).day.at('12:00').do(start_the_draw_santa)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except requests.exceptions.ReadTimeout:
        time.sleep(3)
        text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nПревышено время ожидания запроса'
        # bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text)
        print(text)
    except requests.ConnectionError as error_connection:
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
              f'Тип исключения: <{requests.ConnectionError.__name__}>\n'
              f'Ошибка: {error_connection}\n')
        time.sleep(60)
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nПопытка соединения')
    except Exception as e:
        time.sleep(3)

        #  Получить имя модуля в котором сработало исключение
        frm = inspect.trace()[-1]
        file_name = frm[1]
        line_error = frm[2]

        text = (f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                f'Сработало исключение: "{e}"\n'
                f'Имя файла: "{file_name}"\n'
                f'Строка: {line_error}\n')
                # f'Работа остановлена')

        bot.send_message(chat_id=Secret.list_admins.get('Никита'), text=text)
        print(text)
        # break
