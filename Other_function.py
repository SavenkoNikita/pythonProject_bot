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
