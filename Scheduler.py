import random
import time
import datetime

import schedule
import Clear_old_data
import Data
import Notifications
import Read_file


# Уведомление в IT_info и подписчикам о том кто дежурный
def sh_send_dej(sheet_name):
    some_date = Read_file.read_file(sheet_name)['Date 1']
    some_date2 = Read_file.read_file(sheet_name)['Date 2']
    meaning = Read_file.read_file(sheet_name)['Text 3']
    read_type = Read_file.read_file(sheet_name)['Type']
    difference_date = Read_file.read_file(sheet_name)['Dif date']

    if read_type == 'date':
        if difference_date < 0:  # Если событие в прошлом
            Clear_old_data.clear(sheet_name)  # Очистить старые данные
            sh_send_dej(sheet_name)  # Перезапустить функцию
        elif difference_date == 1:  # Если дата события завтра
            text_day = 'В период с ' + str(some_date.strftime("%d.%m.%Y")) + ' по ' + \
                       str(some_date2.strftime("%d.%m.%Y")) + ' '  # Период дежурства
            text_who = ' будет дежурить ' + meaning + '.'  # Имя следующего дежурного
            end_text = str(text_day) + str(text_who)  # Объединяем строки выше в одну
            Notifications.notification_for('► ДЕЖУРНЫЙ ◄' + '\n' + end_text, sheet_name, 'notification', 'yes')
            print('► ДЕЖУРНЫЙ ◄' + '\n' + end_text)
        elif difference_date > 1:  # Если до даты события больше 1 дня
            print('Рано уведомлять' + '\n')
    elif read_type == 'incorrect':
        end_text = some_date
        print(end_text + '\n')
    elif read_type == 'none':
        end_text = some_date
        print(end_text + '\n')
    else:
        end_text = 'Ошибка чтения данных Dej'
        print(end_text + '\n')
    return


# sh_send_dej()

# Уведомление в GateKeepers о том кто на инвентаризацию
def sh_send_invent(sheet_name):
    # list_name = Data.sheets_file['Инвертаризация']  # Получаем имя страницы по ключу
    # some_date = Read_file.read_file(sheet_name)['Date 1']
    meaning2 = Read_file.read_file(sheet_name)['Text 2']
    read_type = Read_file.read_file(sheet_name)['Type']
    difference_date = Read_file.read_file(sheet_name)['Dif date']

    if read_type == 'date':
        if difference_date < 0:  # Если событие в прошлом
            Clear_old_data.check_relevance(sheet_name)  # Очистить старые данные
            sh_send_invent(sheet_name)  # Перезапустить функцию
        elif 0 <= difference_date <= 5:
            # Склоняем "день"
            def count_day():
                dd = ''
                if difference_date == 0:
                    dd = 'Сегодня инвертаризация.'
                elif difference_date == 1:
                    dd = 'До предстоящей инвентаризации остался 1 день.'
                elif 1 < int(difference_date) <= 4:
                    dd = 'До предстоящей инвентаризации осталось ' + str(difference_date) + ' дня.'
                elif difference_date == 5:
                    dd = 'До предстоящей инвентаризации осталось ' + str(difference_date) + ' дней.'
                # elif difference_date > 5:
                #     dd = 'Следующая инвентаризация состоится ' + str(some_date.strftime("%d.%m.%Y")) + '.'

                return dd

            text_day = count_day()  # Кол-во дней до инвентаризации
            text_who = 'Судя по графику, выходит ' + meaning2 + '.'  # Имя следующего дежурного
            end_text = text_day + '\n' + text_who  # Объединяем строки выше в одну
            Notifications.notification_for('⌚ ИНВЕНТАРИЗАЦИЯ ⌚' + '\n' + end_text, sheet_name, 'notification', 'yes')
            print(end_text)
    elif read_type == 'incorrect':
        end_text = str(Read_file.read_file(sheet_name)['Error'])
        print('Ошибка в листе' + sheet_name + ':' + '\n' + end_text)
    elif read_type == 'none':
        end_text = str(Read_file.read_file(sheet_name)['Error'])
        print('Ошибка в листе' + sheet_name + ':' + '\n' + end_text)
    else:
        end_text = 'Ошибка чтения данных Invent'
        print('Ошибка в листе' + sheet_name + ':' + '\n' + end_text)


# Кто сегодня закрывает сигналы
def sh_random_name():
    if datetime.datetime.today().isoweekday() <= 5:
        list_name = ['Паша', 'Дима', 'Никита']
        r_name = random.choice(list_name)
        end_text = 'Случайным образом определено, что сигналы сегодня закрывает ' + r_name
        Data.bot.send_message(chat_id=Data.list_groups.get('GateKeepers'), text=end_text)
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)  # Для тестов


# Уведомления для всех
# def sh_notification_all_reg():
#     list_name = Data.sheets_file['Уведомления для всех']
#     some_date = Read_file.read_file(list_name)['Date 1']
#     read_type = Read_file.read_file(list_name)['Type']
#     difference_date = Read_file.read_file(list_name)['Dif date']
#
#     if read_type == 'date':  # Если return в Read_file.py возвращает дату то
#         if difference_date < 0:  # Если событие в прошлом
#             Clear_old_data.clear(list_name)  # Очистить старые данные
#             sh_notification_all_reg()  # Перезапустить функцию
#         elif difference_date == 0:  # Если дата уведомления сегодня
#             Notifications.notification_all_reg(Notifications.notifications())  # Уведомление для всех
#             print(Notifications.notifications())
#         elif difference_date > 0:  # Если дата не наступила
#             print('Рано уведомлять')
#     else:  # Если return в Read_file.py возвращает НЕ дату то
#         # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'),
#         #                       text=Notifications.notifications())  # Отправить сообщение
#         print(some_date)
#     return


def sh_notification(sheet_name):
    some_date = Read_file.read_file(sheet_name)['Date 1']  # Дата во 2й строке 1го столбца
    read_type = Read_file.read_file(sheet_name)['Type']  # Тип данных в ячейке some_date
    difference_date = Read_file.read_file(sheet_name)['Dif date']  # Разница между текущей датой и указанной в some_date

    if read_type == 'date':  # Если return в Read_file.py возвращает дату то
        if difference_date < 0:  # Если событие в прошлом
            Clear_old_data.clear(sheet_name)  # Очистить старые данные
            sh_notification(sheet_name)  # Перезапустить функцию
        elif difference_date == 0:  # Если дата уведомления сегодня
            if sheet_name in Data.sheets_file:
                if sheet_name == 'Уведомления для всех':
                    function = Notifications.notification_all_reg(Notifications.notifications(sheet_name), sheet_name)
                elif sheet_name == 'Уведомления для подписчиков':
                    function = Notifications.notification_for(Notifications.notifications(sheet_name), sheet_name,
                                                              'notification', 'yes')
                elif sheet_name == 'Уведомления для админов':
                    function = Notifications.notification_for(Notifications.notifications(sheet_name), sheet_name,
                                                              'status', 'admin')
                elif sheet_name == 'Инвентаризация':
                    function = sh_send_invent(sheet_name)
                else:
                    print('В файле нет страницы с названием ' + sheet_name)
                function  # Выполняемая функция
                print(function)
        elif difference_date > 0:  # Если дата не наступила
            print('Отчёт sh_notification:\n')
            print('В ' + sheet_name + ' рано уведомлять')
    else:  # Если return в Read_file.py возвращает НЕ дату то
        print(some_date)
    return


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
        time.sleep(60)  # Задержка в секундах
        i += 1


schedule.every().day.at('16:00').do(sh_send_dej, 'Дежурный')  # Проверяет и уведомляет о дежурном

schedule.every().day.at('07:00').do(sh_queue)

# schedule.every().day.at('07:00').do(sh_send_invent)

# schedule.every().day.at('07:01').do(sh_random_name)

while True:
    schedule.run_pending()
    time.sleep(1)
