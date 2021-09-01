from datetime import date

current_date = date.today()
current_date.weekday()


def weekday_now():
    wn = ''
    if current_date.weekday() == 0:
        wn = 'Понедельник'
    elif current_date.weekday() == 1:
        wn = 'Втроник'
    elif current_date.weekday() == 2:
        wn = 'Среда'
    elif current_date.weekday() == 3:
        wn = 'Четверг'
    elif current_date.weekday() == 4:
        wn = 'Пятница'
    elif current_date.weekday() == 5:
        wn = 'Суббота'
    elif current_date.weekday() == 6:
        wn = 'Воскресенье'
    else:
        print('Не могу определить день недели')

    return wn