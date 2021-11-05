import datetime
import urllib

from openpyxl import load_workbook
from smb.SMBHandler import SMBHandler
import urllib.request

import Data

opener = urllib.request.build_opener(SMBHandler)
file_name = opener.open(Data.route)
wb = load_workbook(file_name)  # Открываем нужную книгу
sheet = wb['Дежурный']  # Получить лист по ключу
column_a = sheet['A']

now_date = datetime.datetime.now()  # Получаем текущую дату
now_date_format = now_date.strftime("%d.%m.%Y")


for i in range(len(column_a)):
    if i is not None:
        if isinstance(column_a[i].value, datetime.datetime):
            a = column_a[i].value
            a_format = a.strftime("%d.%m.%Y")
            dd = a - now_date
            dd = dd.days + 1
            # print(a_format)
            # print(now_date_format)
            # print(dd)
            # print('\n')
            if dd < 2:
                print(a_format)

