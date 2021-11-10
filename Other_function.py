import datetime
import os
import time
import urllib

from openpyxl import load_workbook
from smb.SMBHandler import SMBHandler
import urllib.request

import Data
import SQLite


def get_key(d, value):  # Проверяет среди словаря есть ли в нём такое имя и возвращает соответствующий id telegram
    key = 'Имя не найдено или человек не относится к дежурным. Error Other_function.get_key.'
    for k, v in d.items():
        for a in v:
            if a == value:
                key = k
    return key


# print(get_key(Data.user_data, 'впо'))


def get_data_user_SQL(d, value):
    id_telegram = get_key(d, value)  # Присваиваем id из get_key
    print(id_telegram)
    if id_telegram is not None:  # Если id есть то
        if SQLite.check_for_existence(id_telegram) == 'True':  # Если в SQL есть такой id
            end_text = SQLite.get_user_info(id_telegram)  # Получаем склейку <имя + @юзернейм>
            print(end_text)
    return end_text


# get_data_user_SQL(Data.user_data, 'Никита')

def read_sheet(sheet_name):
    opener = urllib.request.build_opener(SMBHandler)
    file_name = opener.open(Data.route)
    wb = load_workbook(file_name)  # Открываем нужную книгу
    sheet = wb[sheet_name]  # Получить лист по ключу
    column_a = sheet['A']  # Колонка A
    # column_b = sheet['B']  # Колонка B
    # column_c = sheet['C']  # Колонка C

    now_date = datetime.datetime.now()  # Получаем текущую дату
    date_list = []  # Объявляем пустой список
    count = 0
    if column_a is not None:  # Если в колонке А не пусто
        for i in range(len(column_a)):  # Повторить для каждого значения в колонке А
            if i is not None:  # Если значение не пустое
                if isinstance(column_a[i].value, datetime.datetime):  # Если значение == дата
                    value_one = column_a[i].value  # Получаем первое значение
                    value_one_column = column_a[i].column  # Колонка значения 1й даты
                    value_one_row = column_a[i].row  # Строка значения 1й даты
                    value_two = sheet.cell(row=value_one_row, column=(value_one_column + 1)).value  # Второе значение
                    difference_date = value_one - now_date  # Разница между 1й датой и сегодня
                    difference_date = difference_date.days + 1  # Форматируем в кол-во дней +1
                    if isinstance(value_two, datetime.datetime):  # Если 2е значение дата
                        meaning = sheet.cell(row=value_one_row, column=(value_one_column + 2)).value  # Значит 3е
                        # значение по координатам находится рядом со вторым
                    else:
                        meaning = value_two  # Иначе <событие> находится во второй колонке

                    if difference_date >= 0:  # Если событие сегодня или в будущем
                        count = count + 1
                        if isinstance(value_two, datetime.datetime):  # Если 2е значение является датой
                            date_list.append([value_one, value_two, meaning])  # Заполняем список списками из 3х данных
                        else:
                            date_list.append([value_one, meaning])  # Заполняем список списками из 2х данных
                    elif difference_date < -1:  # Если дата в прошлом
                        sheet.delete_rows(value_one_row)  # Удаляем указанную в скобках строку
                        wb.save('test.xlsx')  # Сохранить книгу
                        file = open('test.xlsx', 'rb')
                        file_name = opener.open(Data.route, data=file)
                        file_name.close()
                        os.remove('test.xlsx')
                        del_data = '• Со страницы ' + str(sheet) + ' удалены данные'
                        print(del_data)
                        read_sheet(sheet_name)
            else:
                print('Данные отсутствуют')

    date_list.sort()  # Сортируем лист по дате
    date_list_today = []

    if len(date_list) > 0:  # Если список содержит хотябы 1 запись
        if count >= 1:
            for i in range(count):  # Повторить для каждого значения
                if len(date_list[i]) == 2:  # Если 1й список в списке date_list содержит 2 значения
                    date = date_list[i][0]  # 1е значение записываем как дата
                    event = date_list[i][1]  # 2е значение <событие>
                    event_data = [date, event]  # Создаём список из этих 2х значений
                    date_list_today.append(event_data)
                elif len(date_list[i]) == 3:  # Если 1й список в списке date_list содержит 3 значения
                    first_date = date_list[i][0]  # 1е значение записываем как дата
                    last_date = date_list[i][1]  # 2е значение записываем как дата
                    event = date_list[i][2]  # 3е значение <событие>
                    event_data = [first_date, last_date, event]  # Создаём список из этих 3х значений
                    date_list_today.append(event_data)
                # print(date_list_today)
                return date_list_today  # Возвращаем список
    else:  # Если нет ни одной записи
        pass  # Ничего не делать

    return


# read_sheet('Дежурный')
# read_sheet('Уведомления для подписчиков')
