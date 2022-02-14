class Counter:
    """Класс считает различные сущности"""

    # def __init__(self):

    def days_before_inventory(self, number):
        """Осталось дней до инвентаризации"""
        stayed = ['остался', 'осталось']
        days = ['день', 'дня', 'дней']

        if number == 0:
            return 'Сегодня инвентаризация.'
        elif number % 10 == 1 and number % 100 != 11:
            s = 0
            d = 0
            return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d] + '.'
        elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
            s = 1
            d = 1
            return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d] + '.'
        else:
            s = 1
            d = 2
            return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d] + '.'

    def number_of_events(self, number):
        """Количество записей"""
        records = ['запись', 'записи', 'записей']

        if number == 0:
            return 'К сожалению, нет данных о предстоящих дежурствах.'
        elif number % 10 == 1 and number % 100 != 11:  # <1, 21 запись>
            r = 0
            return 'На данный момент есть ' + str(number) + ' ' + records[r] + '. Сколько событий показать?'
        elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):  # <3, 22 записи>
            r = 1
            return 'На данный момент есть ' + str(number) + ' ' + records[r] + '. Сколько событий показать?'
        else:  # <5, 47 записей>
            r = 2
            return 'На данный момент есть ' + str(number) + ' ' + records[r] + '. Сколько событий показать?'
