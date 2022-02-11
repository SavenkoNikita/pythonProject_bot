class Counter:
    """Класс считает различные сущности"""

    # def __init__(self):

    def days_before_inventory(self, number):
        stayed = ['остался', 'осталось']
        days = ['день', 'дня', 'дней']

        if number == 0:
            return 'Сегодня инвентаризация.'
        elif number % 10 == 1 and number % 100 != 11:
            s = 0
            d = 0
            return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d]
        elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
            s = 1
            d = 1
            return 'До предстоящей инвентаризации ' + stayed[s] + ' ' + str(number) + ' ' + days[d]

