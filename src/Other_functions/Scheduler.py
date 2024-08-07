import datetime
import inspect
import random
import time

import requests
import schedule

from Tests.Test_2 import test
from src.Body_bot import Secret
from src.Body_bot.Secret import bot, list_admins
from src.Other_functions.File_processing import (check_event_for_all_users,
                                                 check_event_for_notif_users, check_event_for_admins,
                                                 check_event_for_subs_bar, check_event_invent, check_dej)
from src.Other_functions.Functions import SQL, name_hero
from src.Other_functions.Tracking_devices import TrackingSensor
from src.Other_functions.Working_with_notifications import Notification

developer = list_admins.get('Никита')


def top_statistic():
    text_top_user = SQL().top_chart()
    bot.send_message(chat_id=developer,
                     text=text_top_user,
                     disable_notification=True)


def check_top_byers(silent=True):
    """Если сегодня 1-е число месяца создаёт рейтинг барахольщиков за всё время."""
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


def schedule_next_run():
    """Обновляет расписание заданий"""

    def create_random_time(summary=None, name_func='?'):
        hour = '{:02d}'.format(random.randint(00, 23))

        if summary == 'first summary':
            """Формирует время <07:random(0:59)>"""
            hour = '07'
        elif summary == 'second summary':
            """Формирует время <08:random(0:59)>"""
            hour = '08'
        elif summary == 'daily summary':
            """Формирует время <random(14-17):random(0:59)>"""
            hour = '{:02d}'.format(random.randint(14, 17))
        else:
            hour = hour

        minutes = '{:02d}'.format(random.randint(0, 59))
        time_str = f'{hour}:{minutes}'
        print(f'Функция "{name_func}.tag({summary})" должна сработать {datetime.datetime.now().strftime("%d.%m.%Y")} в '
              f'{time_str}')
        return time_str

    print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")} Обновление расписания заданий:')

    list_func = [
        {'first summary': [check_event_invent]},
        {'second summary': [name_hero, check_event_for_notif_users, check_event_for_all_users,
                            check_event_for_admins, check_event_for_subs_bar]},
        {'daily summary': [check_top_byers, the_most_active_user, check_dej]}
    ]

    def create_schedule(list_funcs):
        """Пересоздаёт расписание выполнения заданий по тегам на текущий день"""
        for element in list_funcs:
            for time_of_day, funcs in element.items():
                schedule.clear(time_of_day)  # Clear old time
                print(f'Удалено расписание заданий с тегом "{time_of_day}"')
                for func in funcs:
                    (schedule.every().day.at(create_random_time(summary=time_of_day, name_func=func.__name__)).
                     do(func).
                     tag(time_of_day))

    create_schedule(list_funcs=list_func)


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


def schedule_run_every_minutes(list_func):
    """Создаёт расписание для функций из списка для выполнения их ежеминутно"""
    for func in list_func:
        schedule.every().minutes.do(func)
        print(f'Создано задание для выполнения функции "{func.__name__}" ежеминутно')


list_every_minutes = [
    update_data_sensors,
    SQL().get_list_faulty_sensors,
    SQL().schedule_cancel_booking,
    SQL().schedule_cancel_lot,
    # SQL().schedule_updating_data_on_lots
]

schedule_run_every_minutes(list_every_minutes)

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
        # bot.send_message(chat_id=developer, text=text)
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

        bot.send_message(chat_id=developer, text=text)
        print(text)
        # break
    except Secret.telebot.apihelper.ApiTelegramException as error:
        print(error)
        time.sleep(3)
