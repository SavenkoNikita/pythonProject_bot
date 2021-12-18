import SQLite

# Команды доступные всем
list_command_user = [
    "• Узнать кто дежурит в ближайшие выходные /dezhurnyj",
    "• Подписаться на рассылку /subscribe",
    "• Отказаться от рассылки /unsubscribe",
    "• Стереть все данные о Вас из базы данных /log_out"
]

# Команды доступные админам
list_command_admin = [
    *list_command_user,
    "• Узнать кто следующий на инвентаризацию жми /invent",
    "• Получить случайное имя /random",
    "• Сменить стикер /change_sticker",
    "• Дать пользователю права администратора /set_admin",
    "• Лишить пользователя прав администратора /set_user",
    # "• Создать новое уведомление /create_record",
]


def can_do_it(x):  # Перечисляет строка за строкой всё что есть в списке с переводом строки
    cd = ('\n'.join(map(str, x)))
    return cd


def can_help(user_id):
    end_text = 'Вот что я умею:' + '\n'
    check_admin = SQLite.check_for_admin(user_id.from_user.id)
    if check_admin is True:  # Если пользователь админ
        end_text = end_text + can_do_it(list_command_admin)  # Передать полный список доступных команд
    else:  # Если пользователь НЕ админ
        end_text = end_text + can_do_it(list_command_user)  # Передать список команд доступных юзеру
    return end_text
