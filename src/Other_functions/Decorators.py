import datetime
import pprint

from src.Other_functions.Functions import SQL


def registration_of_actions(func):
    def foo(message):
        name_func = func.__name__
        user_id = message.chat.id
        user_first_name = message.chat.first_name
        user_last_name = message.chat.last_name

        user = f'{user_first_name} {user_last_name} (ID: {user_id})'

        if user_first_name is None:
            user = f'{user_last_name} (ID: {user_id})'
        elif user_last_name is None:
            user = f'{user_first_name} (ID: {user_id})'

        text_message = message.text

        datetime_now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        post = 'Пользователь'
        if SQL().check_for_admin(user_id) is True:
            post = 'Администратор'

        text_print = f'Date and time: {datetime_now}\nFunc name: {name_func}()\n{post} {user}: "{text_message}"'
        print(text_print)
        # result = func(message)

        if SQL().check_for_existence(user_id) is True:  # Проверка на наличие юзера в БД
            SQL().collect_statistical_information(user_id)  # Счётчик активности пользователя
            SQL().update_data_user(user_id, message.chat.first_name, message.chat.last_name,
                                   message.chat.username)  # Обновление данных о пользователе в БД

        # print(message)
        return func(message)
    return foo
