import datetime
import os
import time
import urllib

from openpyxl import load_workbook
from smb.SMBHandler import SMBHandler
import urllib.request

import Classes
import Count
import Data
import logging


def get_key(user_name):
    """Проверяет среди словаря есть ли в нём имя{user_name} и возвращает соответствующий id_telegram"""

    # key = 'Имя не найдено или человек не относится к дежурным. Error Other_function.get_key.'
    for keys, v in Data.user_data.items():
        for a in v:
            if a == user_name:
                key = keys
                return key


def get_data_user_SQL(user_name):
    """Принимает на вход Имя, проверяет есть ли это имя в списке дежурных, если есть, получает user_id, если он есть в
    БД, подтягивает Имя и user_name. Результат - <имя + @username>"""

    id_telegram = get_key(user_name)  # Присваиваем id из get_key
    print(id_telegram)
    if id_telegram is not None:  # Если id есть то
        if Classes.SQL().check_for_existence(id_telegram) is True:  # Если в SQL есть такой id
            end_text = Classes.SQL().get_user_info(id_telegram)  # Получаем склейку <имя + @username>
            print(end_text)
            return end_text


# noinspection PyTypeChecker
def read_sheet(sheet_name):
    opener = urllib.request.build_opener(SMBHandler)
    file_name = opener.open(Data.route)
    wb = load_workbook(file_name)  # Открываем нужную книгу
    sheet = wb[sheet_name]  # Получить лист по ключу
    column_a = sheet['A']  # Колонка A

    now_date = datetime.datetime.now()  # Получаем текущую дату
    date_list = []  # Объявляем пустой список
    count = 0
    if column_a is not None:  # Если в колонке А не пусто
        for i in range(len(column_a)):  # Повторить для каждого значения в колонке А
            if i is not None:  # Если значение не пустое
                if isinstance(column_a[i].value, datetime.datetime):  # Если значение == дата
                    value_one = column_a[i].value  # Получаем первое значение
                    value_one_column = column_a[i].column  # Колонка значения 1‑й даты
                    value_one_row = column_a[i].row  # Строка значения 1‑й даты
                    value_two = sheet.cell(row=value_one_row, column=(value_one_column + 1)).value  # Второе значение
                    difference_date = value_one - now_date  # Разница между 1‑й датой и сегодня
                    difference_date = difference_date.days + 1  # Форматируем в кол-во дней +1
                    if isinstance(value_two, datetime.datetime):  # Если 2‑е значение дата
                        meaning = sheet.cell(row=value_one_row, column=(value_one_column + 2)).value  # Значит 3‑е
                        # значение по координатам находится рядом со вторым
                    else:
                        meaning = value_two  # Иначе <событие> находится во второй колонке
                    if difference_date >= 0:  # Если событие сегодня или в будущем
                        count = count + 1
                        if isinstance(value_two, datetime.datetime):  # Если 2‑е значение является датой
                            date_list.append([value_one, value_two, meaning])  # Заполняем список списками из 3‑х данных
                        else:
                            date_list.append([value_one, meaning])  # Заполняем список списками из 2‑х данных
                    elif difference_date < -1:  # Если событие было вчера
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

    if len(date_list) > 0:  # Если список содержит хотя бы 1 запись
        if count >= 1:
            for i in range(count):  # Повторить для каждого значения
                if len(date_list[i]) == 2:  # Если 1‑й список в списке date_list содержит 2 значения
                    date = date_list[i][0]  # 1‑е значение записываем как дата
                    event = date_list[i][1]  # 2‑е значение <событие>
                    event_data = [date, event]  # Создаём список из этих 2‑х значений
                    date_list_today.append(event_data)
                elif len(date_list[i]) == 3:  # Если 1‑й список в списке date_list содержит 3 значения
                    first_date = date_list[i][0]  # 1‑е значение записываем как дата
                    last_date = date_list[i][1]  # 2‑е значение записываем как дата
                    event = date_list[i][2]  # 3‑е значение <событие>
                    event_data = [first_date, last_date, event]  # Создаём список из этих 3‑х значений
                    date_list_today.append(event_data)
                return date_list, date_list_today  # Возвращаем списки
    else:  # Если нет ни одной записи
        pass  # Ничего не делать

    return


def logging_event(condition, text):
    if text is not None:
        logging.basicConfig(filename=Data.way_to_log_file, level=logging.INFO,
                            format="%(asctime)s - [%(levelname)s] - %(message)s")
        if condition == 'debug':
            logging.debug(text)
        elif condition == 'info':
            logging.info(text)
        elif condition == 'warning':
            logging.warning(text)
        elif condition == 'error':
            logging.error(text)
        elif condition == 'critical':
            logging.critical(text)


class File_processing:
    """Обработка файла"""

    def __init__(self, sheet_name):
        self.sheet_name = sheet_name
        self.opener = urllib.request.build_opener(SMBHandler)
        self.file_name = self.opener.open(Data.route)
        self.wb = load_workbook(self.file_name)  # Открываем нужную книгу
        self.sheet = self.wb[sheet_name]  # Получить лист по имени
        self.now_date = datetime.datetime.now()  # Получаем текущую дату
        if (self.sheet.cell(row=1, column=1).value and
            self.sheet.cell(row=1, column=2).value and
            self.sheet.cell(row=1, column=3).value) is not None:  # Если заполнены 3 колонки

            self.count_meaning = 3  # Количество непустых колонок 3
        else:
            self.count_meaning = 2  # Количество непустых колонок 2

    def difference_date(self, date):
        f"""На вход принимает дату. Возвращает разницу в днях между сегодня и {date}. Где "1" означает "завтра" и тд"""

        difference = date - self.now_date  # Разница между 1‑й датой и сегодня
        difference = difference.days + 1  # Форматируем в кол-во дней +1

        return difference

    def read_file(self):
        """Возвращает списки значений в формате [ДД.ММ.ГГГГ, ДД.ММ.ГГГГ, событие]. Если дата в списке одна, то
        соответственно [ДД.ММ.ГГГГ, событие]."""

        self.clear_old_data()

        date_list = []  # Объявляем пустой список

        for i in range(1, self.sheet.max_row):  # Повторить для каждого значения в колонке А
            if i is not None:  # Если значение не пустое
                if isinstance(self.sheet.cell(row=i, column=1).value, datetime.datetime):  # Если значение == дата
                    if self.count_meaning == 2:
                        date = self.sheet.cell(row=i, column=1).value  # .strftime("%d.%m.%Y")
                        meaning = self.sheet.cell(row=i, column=2).value
                        line = [date, meaning]
                        date_list.append([line])
                    elif self.count_meaning == 3:
                        date_one = self.sheet.cell(row=i, column=1).value  # .strftime("%d.%m.%Y")
                        date_two = self.sheet.cell(row=i, column=2).value  # .strftime("%d.%m.%Y")
                        meaning = self.sheet.cell(row=i, column=3).value
                        line = [date_one, date_two, meaning]
                        date_list.append(line)

        date_list.sort()  # Сортируем лист по дате

        if len(date_list) == 0:
            print(f'Список <{self.sheet_name}> пуст')
            return None
        else:
            return date_list

    def clear_old_data(self):
        """Очистка неактуальных данных"""

        for i in range(1, self.sheet.max_row):  # Повторить для каждого значения в колонке А
            if i is not None:  # Если значение не пустое
                if isinstance(self.sheet.cell(row=i, column=1).value, datetime.datetime):  # Если значение == дата
                    if self.difference_date(self.sheet.cell(row=i, column=1).value) < 0:
                        date_event = self.sheet.cell(row=i, column=1).value
                        event = self.sheet.cell(row=i, column=self.count_meaning).value
                        print(f'Удалена строка {date_event.row}\n'
                              f'Дата: {date_event}\n'
                              f'Текст: {event}\n\n')
                        self.sheet.delete_rows(i)  # Удаляем указанную в скобках строку
                        self.wb.save('test.xlsx')  # Сохранить книгу
                        file = open('test.xlsx', 'rb')
                        self.file_name = self.opener.open(Data.route, data=file)
                        self.file_name.close()
                        os.remove('test.xlsx')
                        time.sleep(1)
                        self.clear_old_data()
                    else:
                        continue

    def next_dej(self):
        """Если файл заполнен, возвращает строку 'В период с {first_date} по {second_date} будет дежурить {name}.'"""

        if self.sheet_name == 'Дежурный':
            self.clear_old_data()
            if self.read_file() is not None:
                name_from_SQL = Classes.SQL().get_user_info(get_key(self.read_file()[0][2]))
                text_message = f'В период с {self.read_file()[0][0].strftime("%d.%m.%Y")} ' \
                               f'по {self.read_file()[0][1].strftime("%d.%m.%Y")} ' \
                               f'будет дежурить {name_from_SQL}.'
                return text_message

    def sticker_next_dej(self):
        """Сравнивает имя из файла с БД, и если есть совпадение и в БД содержится стикер то вернёт его."""

        self.clear_old_data()
        if self.read_file() is not None:
            sticker = Classes.SQL().get_user_sticker(get_key(self.sheet.cell(row=2, column=self.count_meaning).value))
            if sticker is not None:
                return sticker
            else:
                return None

        # if self.count_meaning == 3:
        #     sticker = Classes.SQL().get_user_sticker(get_key(self.sheet.cell(row=2, column=self.count_meaning).value))
        #     if sticker is not None:
        #         return sticker
        #     else:
        #         return None
        # elif self.count_meaning == 2:
        #     sticker = Classes.SQL().get_user_sticker(get_key(self.sheet.cell(row=2, column=self.count_meaning).value))
        #     if sticker is not None:
        #         return sticker
        #     else:
        #         return None

    # def dej_tomorrow(self):
    #     """Проверяет, идёт кто завтра на инвент или есть ли дежурный"""
    #
    #     if self.difference_date == 1:
    #         if self.sheet_name == 'Дежурный':
    #             return self.next_dej()
    #         elif self.sheet_name == 'Инвентаризация':
    #             self.next_invent()
    #     else:
    #         print('На завтра событий нет')

    def list_dej(self):
        """Возвращает список всех дежурных, что есть в списке"""

        list_dej = []
        for i in self.read_file():
            if self.sheet_name == 'Дежурный':
                if i is not None:
                    date_one = i[0].strftime("%d.%m.%Y")
                    date_two = i[1].strftime("%d.%m.%Y")
                    name_from_SQL = Classes.SQL().get_user_info(get_key(i[2]))
                    text_message = f'В период с {date_one} по {date_two} будет дежурить {name_from_SQL}.'
                    list_dej.append(text_message)

        return list_dej

    def next_invent(self):
        """Если файл заполнен, возвращает строку 'До предстоящей инвентаризации осталось {N} дней.
        Судя по графику, выходит {name}'"""

        if self.sheet_name == 'Инвентаризация':
            if self.read_file() is not None:
                name_from_SQL = Classes.SQL().get_user_info(get_key(self.sheet.cell(row=2, column=2).value))
                dead_line_date = self.difference_date(self.sheet.cell(row=2, column=1).value)
                dead_line_text = Count.Counter().days_before_inventory(dead_line_date)
                text_who = f'Судя по графику, выходит {name_from_SQL}.'  # Имя следующего дежурного
                text_message = f'{dead_line_text} {text_who}'
                return text_message
            elif self.read_file() is None:
                text_message = 'Нет данных об этом. Необходимо заполнить файл!'
                return text_message

    def check_event_today(self):
        """Проверяет есть ли сегодня событие. Результат - уведомление соответствующей группе пользователей."""

        if self.read_file() is not None:
            for i in range(1, self.sheet.max_row):
                if self.sheet_name in Data.sheets_file:
                    if isinstance(self.sheet.cell(row=i, column=1).value, datetime.datetime):  # Если значение == дата
                        if self.difference_date(self.sheet.cell(row=i, column=1).value) == 0:
                            if self.sheet_name == 'Уведомления для всех':
                                text_message = f'• Уведомление для зарегистрированных пользователей •\n\n' \
                                               f'{self.sheet.cell(row=i, column=2).value}'
                                print(text_message)
                                Classes.Notification().all_registered(text_message)
                                # Data.bot.send_message(Data.list_admins.get('Никита'), text_message)
                            elif self.sheet_name == 'Уведомления для подписчиков':
                                text_message = f'• Уведомление для подписчиков •\n\n' \
                                               f'{self.sheet.cell(row=i, column=2).value}'
                                print(text_message)
                                Classes.Notification().notification_for(text_message, 'notification', 'yes')
                                # Data.bot.send_message(Data.list_admins.get('Никита'), text_message)
                            elif self.sheet_name == 'Уведомления для админов':
                                text_message = f'• Уведомление для администраторов •\n\n' \
                                               f'{self.sheet.cell(row=i, column=2).value}'
                                print(text_message)
                                Classes.Notification().notification_for(text_message, 'status', 'admin')
                                # Data.bot.send_message(Data.list_admins.get('Никита'), text_message)
                        elif self.difference_date(self.sheet.cell(row=i, column=1).value) == 1:
                            if self.sheet_name == 'Дежурный':
                                text_message = self.next_dej()
                                name_dej = self.sheet.cell(row=i, column=3).value
                                print(text_message)
                                Classes.Notification().notification_for(text_message, 'notification', 'yes')
                                Classes.Notification().send_sticker_for(name_dej, 'notification', 'yes')
                                # Data.bot.send_message(Data.list_admins.get('Никита'), text_message)
                            elif self.sheet_name == 'Инвентаризация':
                                self.next_invent()
                        elif self.difference_date(
                                self.sheet.cell(row=i, column=1).value) >= 1:  # Если дата не наступила
                            if self.count_meaning == 2:
                                print(f'{str(File_processing.check_event_today.__qualname__)}\n'
                                      f'Событие не наступило\nЛист:{self.sheet_name}\n'
                                      f'Текст уведомления:{self.sheet.cell(row=i, column=2).value}\n'
                                      f'Дата:{self.sheet.cell(row=i, column=1).value.strftime("%d.%m.%Y")}\n\n')
                            elif self.count_meaning == 3:
                                print(f'{str(File_processing.check_event_today.__qualname__)}\n'
                                      f'Событие не наступило\nЛист:{self.sheet_name}\n'
                                      f'Текст уведомления:{self.sheet.cell(row=i, column=3).value}\n'
                                      f'Дата:{self.sheet.cell(row=i, column=1).value.strftime("%d.%m.%Y")}\n\n')

                        # time.sleep(5)

    def create_event(self, date, text_event):
        """Принимает дату и текст уведомления и записывает в файл. Возвращает текст с описанием созданного
        уведомления """

        # i = 0
        try:
            for i in range(1, self.sheet.max_row):  # Повторить для каждого значения в колонке А
                if self.sheet.cell(row=i, column=1).value is None:
                    print(f'Строка {self.sheet.cell(row=i, column=1).row} пустая')
                    empty_string = self.sheet.cell(row=i, column=1).row
                    self.sheet.cell(row=empty_string, column=1).value = date  # Дата
                    self.sheet.cell(row=empty_string, column=2).value = text_event  # Текст события
                    self.wb.save('test.xlsx')  # Сохранить книгу
                    file = open('test.xlsx', 'rb')
                    self.file_name = self.opener.open(Data.route, data=file)
                    self.file_name.close()
                    os.remove('test.xlsx')
                    text_message = f'• Запись добавлена в лист: <{self.sheet_name}>\n' \
                                   f'• Дата уведомления: <{date}>\n' \
                                   f'• Текст: <{text_event}>\n'

                    return text_message
        except Exception as e:
            # time.sleep(3)
            print(str(e))
            # Other_function.logging_event('error', str(e))
