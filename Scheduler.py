import random
import time
import datetime

import schedule
import Data
import Notifications
import Other_function
import SQLite


# Уведомление подписчиков о том кто дежурный
def sh_send_dej(sheet_name):
    if Other_function.read_sheet(sheet_name) is not None:
        date_list_today = Other_function.read_sheet(sheet_name)[1]
        event_data = date_list_today[0]

        first_date = event_data[0]
        first_date_format = first_date.strftime("%d.%m.%Y")

        last_date = event_data[1]
        last_date_format = last_date.strftime("%d.%m.%Y")

        event = event_data[2]

        date_now = datetime.datetime.now()  # Получаем текущую дату
        difference_date = first_date - date_now
        difference_date = difference_date.days + 1

        name_from_SQL = SQLite.get_user_info(Other_function.get_key(Data.user_data, event))
        if name_from_SQL is None:
            name_from_SQL = event
        text_message = 'В период с ' + first_date_format + ' по ' + last_date_format + ' ' + 'будет дежурить ' + \
                       name_from_SQL + '.'

        if difference_date == 1:
            # Если в БД у пользователя содержится стикер
            if SQLite.get_user_sticker(Other_function.get_key(Data.user_data, event)) is not None:
                # Пришлёт сообщение о дежурном
                Notifications.notification_for(text_message, 'notification', 'yes')
                # Пришлёт стикер этого дежурного
                Notifications.send_sticker_for(event, 'notification', 'yes')
                # Data.bot.send_message(1827221970, text_message)
            else:
                # Пришлёт сообщение о дежурном
                Notifications.notification_for(text_message, 'notification', 'yes')
                # Data.bot.send_message(1827221970, text_message)
            print('Отчет sh_send_dej:\n' + text_message + '\n')
        else:
            print('Отчет sh_send_dej:\n Завтра дежурных нет!\n')
    else:
        print('Отчет sh_send_dej:\n На странице <' + sheet_name + '> отсутствуют данные!\n')


# Уведомление в
def sh_send_invent(sheet_name):
    if Other_function.read_sheet(sheet_name) is not None:
        date_list_today = Other_function.read_sheet(sheet_name)[1]
        event_data = date_list_today[0]

        first_date = event_data[0]
        # first_date_format = first_date.strftime("%d.%m.%Y")

        event = event_data[1]

        name_from_SQL = SQLite.get_user_info(Other_function.get_key(Data.user_data, event))
        if name_from_SQL is None:
            name_from_SQL = event
        date_now = datetime.datetime.now()  # Получаем текущую дату
        difference_date = first_date - date_now
        difference_date = difference_date.days + 1
        # print(name_from_SQL)

        # Склоняем "день"
        def count_day():
            dd = ''
            if difference_date == 0:
                dd = 'Сегодня инвертаризация.'
            elif difference_date == 1:
                dd = 'До предстоящей инвентаризации остался 1 день.'
            elif 1 < difference_date <= 4:
                dd = 'До предстоящей инвентаризации осталось ' + str(difference_date) + ' дня.'
            elif difference_date == 5:
                dd = 'До предстоящей инвентаризации осталось 5 дней.'
            # elif difference_date > 5:
            #     dd = 'Следующая инвентаризация состоится ' + str(first_date_format) + '.'
            return dd

        text_day = count_day()  # Кол-во дней до инвентаризации
        text_who = 'Судя по графику, выходит ' + name_from_SQL + '.'  # Имя следующего дежурного
        text_message = text_day + '\n' + text_who  # Объединяем строки выше в одну
        # Если
        if 0 <= difference_date <= 5:
            # Если в БД у пользователя содержится стикер
            if SQLite.get_user_sticker(Other_function.get_key(Data.user_data, event)) is not None:
                # Пришлёт сообщение о дежурном
                Notifications.notification_for(text_message, 'status', 'admin')
                # Пришлёт стикер этого дежурного
                Notifications.send_sticker_for(text_message, 'status', 'admin')
            else:
                # Пришлёт сообщение о дежурном
                Notifications.notification_for(text_message, 'status', 'admin')
            print('Отчет sh_send_invent:\n' + text_message + '\n')
        else:
            print('Отчет sh_send_invent:\n В ближайшее время на инвент никто не идёт!\n')
    else:
        print('Отчет sh_send_invent:\n На странице <' + sheet_name + '> отсутствуют данные!\n')


# Кто сегодня закрывает сигналы
def sh_random_name():
    if datetime.datetime.today().isoweekday() <= 5:
        list_name = ['Паша', 'Дима', 'Никита']
        r_name = random.choice(list_name)
        end_text = 'Случайным образом определено, что сигналы сегодня закрывает ' + r_name
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)
        Data.bot.send_message(chat_id=Data.list_admins.get('Дима'), text=end_text)
        Data.bot.send_message(chat_id=Data.list_admins.get('Паша'), text=end_text)


def sh_notification(sheet_name):
    if Other_function.read_sheet(sheet_name) is not None:
        date_list = Other_function.read_sheet(sheet_name)[0]
        for i in range(len(date_list)):
            event_data = date_list[i]
            first_date = event_data[0]
            event = event_data[1]
            date_now = datetime.datetime.now()  # Получаем текущую дату
            difference_date = first_date - date_now
            difference_date = difference_date.days + 1

            if difference_date == 0:
                if sheet_name in Data.sheets_file:
                    if event is not None:
                        if sheet_name == 'Уведомления для всех':
                            text_message = '• Уведомление для зарегистрированных пользователей •\n\n' + event
                            Notifications.notification_all_reg(text_message)
                            # Data.bot.send_message(1827221970, text_message)
                        elif sheet_name == 'Уведомления для подписчиков':
                            text_message = '• Уведомление для подписчиков •\n\n' + event
                            Notifications.notification_for(text_message, 'notification', 'yes')
                            # Data.bot.send_message(1827221970, text_message)
                        elif sheet_name == 'Уведомления для админов':
                            text_message = '• Уведомление для администраторов •\n\n' + event
                            Notifications.notification_for(text_message, 'status', 'admin')
                            # Data.bot.send_message(1827221970, text_message)
                        elif sheet_name == 'Инвентаризация':
                            sh_send_invent(sheet_name)
                            # Data.bot.send_message(1827221970, text_message)
                            # print('invent')
                        time.sleep(5)
                else:
                    print('Отчёт sh_notification:')
                    print('В файле нет страницы с названием <' + sheet_name + '>\n')

            elif difference_date > 0:  # Если дата не наступила
                print('Отчёт sh_notification:')
                print('В <' + sheet_name + '> рано уведомлять\n')
                pass

    else:
        text_message = 'На странице <' + sheet_name + '> нет данных для оповещения\n'
        Data.bot.send_message(1827221970, text_message)
        print('Отчёт sh_notification:\n' + text_message)


def sh_queue():
    list_queue = [
        'Уведомления для подписчиков',
        'Уведомления для всех',
        'Уведомления для админов',
        'Инвентаризация'
    ]

    i = 0
    while i < len(list_queue):
        sh_notification(list_queue[i])
        time.sleep(5)  # Задержка в секундах
        i += 1


time_dej = '18:00'
time_other = '08:00'

schedule.every().day.at(time_dej).do(sh_send_dej, 'Дежурный')  # Проверяет и уведомляет о дежурном
schedule.every().day.at(time_other).do(sh_queue)
schedule.every().day.at(time_other).do(sh_random_name)

# sh_queue()

while True:
    schedule.run_pending()
    time.sleep(1)
