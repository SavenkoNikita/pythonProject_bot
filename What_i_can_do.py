import SQLite

# command_user = [
#     '/dezhurnyj'
# ]
#
# command_admin = [
#     *command_user,
#     '/invent',
#     '/random',
#     # '/to_appoint_admin'
# ]

# Команды доступные всем
list_command_user = [
    "• Узнать кто дежурит в ближайшие выходные /dezhurnyj",
    # "• Подписаться на рассылку /subscribe",
    # "• Отказаться от рассылки /unsubscribe"
]

# Команды доступные админам
list_command_admin = [
    *list_command_user,
    "• Узнать кто следующий на инвентаризацию жми /invent",
    "• Получить случайное имя /random",
    # "• Дать пользователю админские права /set_admin",
    # "• Присвоить пользователю статус <user> /set_user",
    # '/set_admin'
]


def can_do_it(x):  # Перечисляет строка за строкой всё что есть в списке с переводом строки
    cd = ('\n'.join(map(str, x)))
    return cd


def can_help(user_id):
    end_text = 'Вот что я умею:' + '\n'
    check_admin = SQLite.check_for_admin(user_id.from_user.id)
    if check_admin == 'True':  # Если пользователь админ
        end_text = end_text + can_do_it(list_command_admin)  # Передать полный список доступных команд
    else:  # Если пользователь НЕ админ
        end_text = end_text + can_do_it(list_command_user)  # Передать список команд доступных юзеру
    return end_text
