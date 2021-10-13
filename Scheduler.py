import random
import time
import datetime

import schedule
import Clear_old_data
import Data
import Notifications
import Read_file


# Уведомление в IT_info и подписчикам о том кто дежурный
def sh_send_dej():
    list_name = Data.sheets_file['Дежурный']
    some_date = Read_file.read_file(list_name)['Date 1']
    some_date2 = Read_file.read_file(list_name)['Date 2']
    meaning = Read_file.read_file(list_name)['Text 3']
    read_type = Read_file.read_file(list_name)['Type']
    difference_date = Read_file.read_file(list_name)['Dif date']

    if read_type == 'date':
        if difference_date <= 0:  # Если событие в прошлом или сегодня
            Clear_old_data.clear(list_name)  # Очистить старые данные
            sh_send_dej()  # Перезапустить функцию
        elif difference_date == 1:  # Если дата события завтра
            text_day = 'В период с ' + str(some_date.strftime("%d.%m.%Y")) + ' по ' + \
                       str(some_date2.strftime("%d.%m.%Y")) + ' '  # Период дежурства
            text_who = ' будет дежурить ' + meaning + '.'  # Имя следующего дежурного
            end_text = str(text_day) + str(text_who)  # Объединяем строки выше в одну
            Notifications.notifications_for_subscribers('► ДЕЖУРНЫЙ ◄' + '\n' + end_text)
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
def sh_send_invent():
    list_name = Data.sheets_file['Инвертаризация']  # Получаем имя страницы по ключу
    some_date = Read_file.read_file(list_name)['Date 1']
    meaning2 = Read_file.read_file(list_name)['Text 2']
    read_type = Read_file.read_file(list_name)['Type']
    difference_date = Read_file.read_file(list_name)['Dif date']

    if read_type == 'date':
        Clear_old_data.check_relevance(list_name)

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
            elif difference_date > 5:
                dd = 'Следующая инвентаризация состоится ' + str(some_date.strftime("%d.%m.%Y")) + '.'

            return dd

        text_day = count_day()  # Кол-во дней до инвентаризации
        text_who = 'Судя по графику, выходит ' + meaning2 + '.'  # Имя следующего дежурного
        end_text = text_day + '\n' + text_who  # Объединяем строки выше в одну
        if 0 <= difference_date <= 5:
            # Data.bot.send_message(chat_id=Data.list_groups.get('GateKeepers'), text=end_text)
            Notifications.notifications_for_admins('⌚ ИНВЕНТАРИЗАЦИЯ ⌚' + '\n' + end_text)
            print(end_text)
    elif read_type == 'incorrect':
        end_text = str(Read_file.read_file(list_name)['Error'])
    elif read_type == 'none':
        end_text = str(Read_file.read_file(list_name)['Error'])
    else:
        end_text = 'Ошибка чтения данных Invent'


# Кто сегодня закрывает сигналы
def sh_random_name():
    if datetime.datetime.today().isoweekday() <= 5:
        list_name = ['Паша', 'Дима', 'Никита']
        r_name = random.choice(list_name)
        end_text = 'Случайным образом определено, что сигналы сегодня закрывает ' + r_name
        Data.bot.send_message(chat_id=Data.list_groups.get('GateKeepers'), text=end_text)
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_text)  # Для тестов


# Уведомления
def sh_notification():
    list_name = Data.sheets_file['Уведомления']
    some_date = Read_file.read_file(list_name)['Date 1']
    read_type = Read_file.read_file(list_name)['Type']
    difference_date = Read_file.read_file(list_name)['Dif date']

    if read_type == 'date':  # Если return в Read_file.py возвращает дату то
        if difference_date < 0:  # Если событие в прошлом
            Clear_old_data.clear(list_name)  # Очистить старые данные
            sh_notification()  # Перезапустить функцию
        elif difference_date == 0:  # Если дата уведомления сегодня
            # Notifications.notification_all_reg(Notifications.notifications())
            Notifications.notifications_for_subscribers(Notifications.notifications())  # Уведомление подписчиков
            print(Notifications.notifications())
        elif difference_date > 0:  # Если дата не наступила
            print('Рано уведомлять')
    else:  # Если return в Read_file.py возвращает НЕ дату то
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'),
        #                       text=Notifications.notifications())  # Отправить сообщение
        print(some_date)
    return


# sh_notification()  # Раскомментировать для тестов

# def sh_test():
#     Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text='test')
#
# schedule.every().second.do(sh_test)


# schedule.every().friday.at('16:00').do(sh_send_dej)
schedule.every().day.at('16:00').do(sh_send_dej)  # Проверяет и уведомляет о дежурном
schedule.every().day.at('07:00').do(sh_send_invent)
# schedule.every().day.at('07:01').do(sh_random_name)
schedule.every().day.at('07:02').do(sh_notification)
# schedule.every(5).seconds.do(sh_send_dej)
# schedule.every(5).seconds.do(sh_send_invent)
# schedule.every(5).seconds.do(sh_notification)
# schedule.every(5).seconds.do(sh_random_name)

# schedule.every().day.at('00:00').do(sh_i_job)
# schedule.every().day.at('00:00').do(Clear_old_data.clear)
# schedule.every(1).minutes.do(Clear_old_data.clear)
# schedule.every(1).minutes.do(sh_notification)


# schedule.every().seconds.do(sh_send_dej)
# schedule.every().thursday.at("15:06").do(job)
# schedule.cancel_job(hello)
# schedule.every().thursday.at("17:20").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
