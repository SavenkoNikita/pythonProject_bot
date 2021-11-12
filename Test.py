import telebot


def test(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'True':  # Проверка на наличие юзера в БД
        SQLite.update_data_user(message)  # Акуализация данных о пользователе в БД
        text_message = 'Что вы хотите получить?\n'
        keyboard = telebot.types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)  # Вызов кнопки
        buttons = ['Имя следующего дежурного', 'Список нескольких дежурных в очереди']
        keyboard.add(*buttons)
        # keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
        bot.send_message(message.from_user.id, text_message, reply_markup=keyboard)  #
        print(text_message + '\n')
        bot.register_next_step_handler(message, test_step_2)  # Регистрация следующего действия
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться, жми /start'
        bot.send_message(message.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


def test_step_2(message):
    try:

    except Exception as e:  # В любом другом случае бот сообщит об ошибке
        bot.reply_to(message, 'Что-то пошло не так. Чтобы попробовать снова, жми /dej')
        print(str(e))

    return