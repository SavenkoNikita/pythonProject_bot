import datetime as datetime
import os
import random
import signal
import sys
import time

import telebot

import Data
import Exchange_with_ERP.Exchange_with_ERP
import Other_functions.File_processing
from Other_functions import Working_with_notifications
from Other_functions.Functions import SQL, can_help, number_of_events, declension_day, \
    logging_telegram_bot

time_now = lambda x: time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(x))  # Конвертация даты в читабельный вид
bot = Data.bot
answer_bot = 'Бот ответил:\n'

log_file = Data.way_to_log_telegram_bot


def full_name_user(message):
    """Принимает на вход сообщение. Возвращает имя пользователя: Администратор/Пользователь + Имя + ID"""

    check_admin = SQL().check_for_admin(message.from_user.id)  # Проверяем является ли пользователь админом
    if check_admin is True:
        status_user = 'Администратор '
    else:
        status_user = 'Пользователь '
    name_user = f'{message.from_user.first_name} (ID: {message.from_user.id})'  # Получаем имя и id
    pattern = f'{time_now(message.date)}\n{status_user} {name_user}'  # Итог дата, /n, статус и данные пользователя
    return pattern


def existence(message):
    if message.forward_from is not None:  # Если сообщение является пересылаемым
        user_id = message.forward_from.id  # Получаем id человека полученного из пересылаемого сообщения
    else:
        user_id = message.from_user.id

    print(f'{full_name_user(message)} отправил команду:\n{message.text}')
    if SQL().check_for_existence(user_id) is True:  # Проверка на наличие юзера в БД
        SQL().collect_statistical_information(user_id)  # Счётчик активности пользователя
        SQL().update_data_user(message)
        if SQL().check_verify_in_ERP(user_id) is True:
            return True
        else:
            verify_error = 'Чтобы воспользоваться функцией необходимо пройти верификацию в 1С -> /verification'
            print(f'{answer_bot}{verify_error}\n')
            return verify_error
    else:
        end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться -> /start'
        print(f'{answer_bot}{end_text}\n')
        return end_text


def rights_admin(message):
    if message.forward_from is not None:  # Если сообщение является пересылаемым
        user_id = message.forward_from.id  # Получаем id человека полученного из пересылаемого сообщения
    else:
        user_id = message.from_user.id

    if existence(message) is True:
        if SQL().check_for_admin(user_id) is True:
            return True
        else:  # Если пользователь не админ, бот сообщит об этом
            end_text = 'У вас нет прав для выполнения этой команды'
            print(f'{answer_bot}{end_text}\n')
            return end_text


def types_message(message):
    """Имитация нажатия клавиш ботом"""

    if message.forward_from is not None:  # Если сообщение является пересылаемым
        user_id = message.forward_from.id
    else:
        user_id = message.from_user.id

    # count_text_message = random.randint(3, 7)  # Случайное кол-во секунд будет имитироваться набор текста
    count_text_message = float(int(0.1))

    bot.send_chat_action(user_id, action='typing')
    time.sleep(count_text_message)


@bot.message_handler(commands=['start'])
def start_command(message):
    """Приветственное сообщение"""

    print(f'{full_name_user(message)} отправил команду:\n{message.text}')
    if SQL().check_for_existence(message.from_user.id) is False:  # Если пользователь отсутствует в БД
        # Приветственное сообщение
        hello_message = f'Добро пожаловать {message.from_user.first_name}!\n' \
                        f'Это информационный бот IT отдела. Тут можно узнать кто из системных администраторов ' \
                        f'дежурный в ближайшие дни, кто и когда отсутствует и прочая информация.\n' \
                        f'Для того чтобы пользоваться функциями бота, необходимо пройти регистрацию нажав /register. ' \
                        f'Тем самым вы даёте согласие на хранение и обработку данных о вашем аккаунте. В базу данных ' \
                        f'будут занесены следующие сведения:\n' \
                        f'ID: {message.from_user.id}\n' \
                        f'Имя: {message.from_user.first_name}\n' \
                        f'Фамилия: {message.from_user.last_name}\n' \
                        f'Username:  @{message.from_user.username}\n'
        types_message(message)
        bot.reply_to(message, hello_message)
        print(f'{answer_bot}{hello_message}\n')
    else:  # Эта строка появится если уже зарегистрированный пользователь попытается заново пройти регистрацию
        end_text = f'Привет еще раз, {message.from_user.first_name}\nМы уже знакомы!\n' \
                   f'Список доступных команд тут -> /help'
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['register'])
def register(message):
    """Регистрация данных о пользователе в БД"""

    print(f'{full_name_user(message)} отправил команду:\n{message.text}')
    if SQL().check_for_existence(message.from_user.id) is False:  # Если пользователь отсутствует в БД
        SQL().db_table_val(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username)
        bot.send_message(chat_id=message.from_user.id,
                         text='Подождите. Сохраняю данные о вас...')
        time.sleep(5)  # Подождать указанное кол-во секунд
        register_message = f'Добро пожаловать {message.from_user.first_name}!\n' \
                           f'Остался последний шаг. Необходимо пройти верификацию в 1С. ' \
                           f'Для этого нажмите сюда -> /verification.'
        # f'Чтобы узнать, что умеет бот, жми /help.\n' \
        # f'Не забудь подписаться на рассылку, чтобы быть в курсе последних событий, жми /subscribe'
        types_message(message)
        bot.reply_to(message, register_message)  # Бот пришлёт уведомление об успешной регистрации
        print(f'{answer_bot}{register_message}\n')
    else:  # Иначе бот уведомит о том что пользователь уже регистрировался
        end_text = f'Вы уже зарегистрированы!\nЧтобы узнать что умеет бот жми /help.'
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['log_out'])
def log_out(message):
    """Удаление данных о пользователе из БД"""

    print(f'{full_name_user(message)} отправил команду:\n{message.text}')
    if SQL().check_for_existence(message.from_user.id) is True:  # Если пользователь присутствует в БД
        SQL().log_out(message.from_user.id)  # Удаление данных из БД
        first_message = 'Подождите...'
        types_message(message)
        bot.reply_to(message, first_message)
        log_out_message = f'До новых встреч {message.from_user.first_name}!\n' \
                          f'Данные о вашем аккаунте успешно удалены!\n' \
                          f'Чтобы снова пользоваться функционалом бота, жми /register.'
        types_message(message)
        bot.reply_to(message, log_out_message)  # Прощальное сообщение
        print(f'{answer_bot}{log_out_message}\n')
    else:  # Иначе бот уведомит о том что пользователь ещё не регистрировался
        end_text = f'Нельзя удалить данные которых нет :)\nЧтобы это сделать, нужно зарегистрироваться!'
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['help'])
def help_command(message):
    """Список доступных команд"""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        keyboard = telebot.types.InlineKeyboardMarkup()  # Вызов кнопки
        keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
        list_commands = can_help(message.from_user.id)
        types_message(message)
        # Показ списка доступных команд и кнопки "Написать разработчику"
        bot.reply_to(message, list_commands, reply_markup=keyboard)
        print(f'{answer_bot}{list_commands}\n')
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_message = existence(message)
        types_message(message)
        bot.reply_to(message, end_message)
        print(f'{answer_bot}{end_message}\n')


@bot.message_handler(commands=['invent'])
def invent(message):
    """Узнать кто следующий на инвентаризацию"""

    list_name = 'Инвентаризация'  # Имя страницы

    if rights_admin(message) is True:
        if Other_functions.File_processing.Working_with_a_file(list_name).read_file() is not None:
            answer_message = Other_functions.File_processing.Working_with_a_file(list_name).next_invent()
            sticker = Other_functions.File_processing.Working_with_a_file(list_name).sticker_next_dej()
            types_message(message)
            bot.reply_to(message, answer_message)
            if sticker is not None:
                bot.send_sticker(message.chat.id, sticker)
            print(f'{answer_bot}{answer_message}\n')
        else:
            answer_message = Other_functions.File_processing.Working_with_a_file(list_name).next_invent()
            types_message(message)
            bot.reply_to(message, answer_message)
            print(f'{answer_bot}{answer_message}\n')
    else:
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['random'])
def random_name(message):
    """Получить случайное имя из сисадминов"""

    if rights_admin(message) is True:
        list_name = ['Паша', 'Дима', 'Никита']  # Список имён
        r_name = random.choice(list_name)  # Получение случайного значения из списка
        types_message(message)
        bot.reply_to(message, r_name)  # Отправка сообщения с рандомным именем
        print(f'{answer_bot}{r_name}\n')
    else:
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['set_admin'])
def set_to_admin(message):
    """Назначить пользователя админом"""

    if rights_admin(message) is True:
        answer_message = 'Чтобы назначить администратора, перешли мне сообщение от этого человека'
        types_message(message)
        bot.reply_to(message, answer_message)  # Бот пришлёт выше указанный текст
        print(f'{answer_bot}{answer_message}\n')
        bot.register_next_step_handler(message, receive_id)  # Регистрация следующего действия
    else:
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


def receive_id(message):
    """Обработка пересланного сообщения"""
    try:
        id_future_admin = message.forward_from.id  # Получаем id человека полученного из пересылаемого сообщения
        first_name_future_admin = str(message.forward_from.first_name)  # Получаем имя будущего админа
        last_name_future_admin = str(message.forward_from.last_name)  # Получаем фамилию будущего админа
        full_name_future_admin = first_name_future_admin + ' ' + last_name_future_admin  # Склеиваем данные воедино
        print(f'{full_name_user(message)} переслал сообщение от пользователя {full_name_future_admin} '
              f'содержащее текст:\n {message.text}')
        answer_text = f'Пользователь <{full_name_future_admin}> добавлен в список администраторов'
        if SQL().check_for_existence(id_future_admin) is True:  # Проверка на наличие человека в БД
            if SQL().check_for_admin(id_future_admin) is False:  # Проверка админ ли юзер
                SQL().set_admin(id_future_admin)  # Обновляем статус нового админа в БД
                types_message(message)
                bot.reply_to(message, answer_text)  # Бот уведомляет об этом того кто выполнил запрос
                print(f'{answer_bot}{answer_text}\n')
                bot.send_message(id_future_admin, f'Администратор <{message.from_user.first_name}> '
                                                  f'предоставил вам права администратора')  # Бот уведомляет
                # пользователя, что такой-то юзер, дал ему права админа
            else:  # Если тот кому предоставляют права уже админ, бот сообщит об ошибке
                end_text = 'Нельзя пользователю дать права администратора, поскольку он им уже является!'
                types_message(message)
                bot.reply_to(message, end_text)
                print(f'{answer_bot}{end_text}\n')
        else:  # Если того кому пытаются дать права нет в БД, бот сообщит об ошибке
            end_text = 'Вы пытаетесь дать права администратора пользователю который отсутствует в базе данных!'
            types_message(message)
            bot.reply_to(message, end_text)
            print(f'{answer_bot}{end_text}\n')
    except Exception as error:  # В любом другом случае бот сообщит об ошибке
        error_text = 'Что-то пошло не так. Чтобы попробовать снова, жми /set_admin'
        types_message(message)
        bot.reply_to(message, error_text)
        print(str(error))
        logging_telegram_bot('error', str(error))

    return


@bot.message_handler(commands=['set_user'])
def set_to_user(message):
    """Лишить пользователя прав администратора"""

    if rights_admin(message) is True:
        answer_message = '• Чтобы пользователю присвоить статус <user>, перешлите мне сообщение от этого человека.\n' \
                         '• Если хотите отказаться от прав админа, в ответ пришлите сообщение с любым текстом.\n' \
                         '• Для отмены операции нажмите "Отмена".'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Отмена']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)  # Бот пришлёт выше указанный текст и клавиатуру
        bot.register_next_step_handler(message, receive_id_user)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


def receive_id_user(message):
    try:
        print(f'{full_name_user(message)} написал:\n{message.text}')
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        if message.text == 'Отмена':
            answer_message = 'Операция прервана.'
            types_message(message)
            bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        else:
            chat_id = message.chat.id  # Получаем id чата
            id_future_user = chat_id  # Получаем id человека полученного из сообщения
            first_name_future_user = str(message.from_user.first_name)  # Получаем имя будущего юзера
            last_name_future_user = str(message.from_user.last_name)  # Получаем фамилию будущего юзера
            full_name_future_user = first_name_future_user + ' ' + last_name_future_user  # Склеиваем данные воедино
            print(f'{full_name_user(message)} переслал сообщение от пользователя {full_name_future_user} '
                  f'содержащее текст:\n {message.text}')
            answer_text = f'Пользователю <{full_name_future_user}> присвоен статус <user>'
            if SQL().check_for_existence(id_future_user) is True:  # Проверка на наличие человека в БД
                if SQL().check_for_admin(id_future_user) is True:  # Проверка админ ли юзер
                    SQL().set_user(id_future_user)  # Обновляем статус нового юзера в БД
                    types_message(message)
                    bot.reply_to(message, answer_text, reply_markup=hide_keyboard)  # Бот уведомляет об этом того кто
                    # выполнил запрос
                    print(f'{answer_bot}{answer_text}\n')
                    bot.send_message(id_future_user, f'Администратор <{message.from_user.first_name}> лишил вас прав '
                                                     f'администратора')  # Бот уведомляет нового юзера, что
                    # пользователь <Имя>, лишил его прав админа
                else:  # Если тот, кого лишают прав админа, уже и так юзер, бот сообщит об ошибке
                    end_text = 'Нельзя пользователю присвоить статус <user> поскольку он им уже является'
                    types_message(message)
                    bot.reply_to(message, end_text, reply_markup=hide_keyboard)
                    print(f'{answer_bot}{end_text}\n')
            else:  # Если того, кого пытаются лишить прав админа, нет в БД, бот сообщит об ошибке
                end_text = 'Вы пытаетесь присвоить пользователю статус <user>, который отсутствует в базе данных!'
                types_message(message)
                bot.reply_to(message, end_text, reply_markup=hide_keyboard)
                print(f'{answer_bot}{end_text}\n')

    except Exception as error:  # В любом другом случае бот сообщит об ошибке
        error_text = 'Что-то пошло не так. Чтобы попробовать снова, жми /set_user'
        types_message(message)
        bot.reply_to(message, error_text)
        print(str(error))
        logging_telegram_bot('error', str(error))
    return


@bot.message_handler(commands=['subscribe'])
def set_subscribe(message):
    """Подписка на рассылку"""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        if SQL().check_status_DB(message.from_user.id, 'notification',
                                 'yes') is False:  # Если пользователь не подписчик
            SQL().change_status_DB(message.from_user.id, 'notification')  # Присвоить статус <подписан>
            end_text = 'Вы подписаны на уведомления. Теперь вам будут приходить уведомления о том кто дежурит в ' \
                       'выходные, кто в отпуске и прочая информация.\n Чтобы отписаться жми /unsubscribe '
            types_message(message)
            bot.reply_to(message, end_text)  # Отправка текста выше
            #  Отсылка уведомлений о действии разработчику
            bot.send_message(chat_id=Data.list_admins.get('Никита'),
                             text=f'{full_name_user(message)} подписался на уведомления.')
            print(f'{answer_bot}{end_text}\n')
        else:  # Если подписчик пытается подписаться, то получит ошибку
            end_text = 'Вы уже подписаны на уведомления.'
            types_message(message)
            bot.reply_to(message, end_text)
            print(f'{answer_bot}{end_text}\n')
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = existence(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['unsubscribe'])
def set_subscribe(message):
    if existence(message) is True:
        if SQL().check_status_DB(message.from_user.id, 'notification',
                                 'yes') is True:  # Если пользователь подписчик
            SQL().change_status_DB(message.from_user.id,
                                   'notification')  # Присвоить в БД статус <не подписан>
            end_text = 'Рассылка отключена.\n Чтобы подписаться жми /subscribe'
            types_message(message)
            bot.reply_to(message, end_text)  # Отправка текста выше
            #  Отсылка уведомлений о действии разработчику
            bot.send_message(chat_id=Data.list_admins.get('Никита'),
                             text=f'{full_name_user(message)} отписался от уведомлений.')
            print(f'{answer_bot}{end_text}\n')
        else:  # Если не подписчик пытается отписаться, то получит ошибку
            end_text = 'Нельзя отказаться от уведомлений на которые не подписан.'
            types_message(message)
            bot.reply_to(message, end_text)
            print(f'{answer_bot}{end_text}\n')
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = existence(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['change_sticker'])
def change_sticker(message):
    """Присвоить/сменить себе стикер"""

    if rights_admin(message) is True:
        answer_message = 'Отправь мне стикер который хочешь привязать в своей учётной записи!'
        types_message(message)
        bot.reply_to(message, answer_message)
        bot.register_next_step_handler(message, change_sticker_step_2)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


def change_sticker_step_2(message):
    print(f'{full_name_user(message)} отправил стикер {message.sticker.file_id}')
    SQL().update_sqlite_table(message.sticker.file_id, message.from_user.id, 'sticker')
    end_text = 'Стикер обновлён'
    types_message(message)
    bot.reply_to(message, end_text)
    print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['dezhurnyj'])
def dej(message):
    """Узнать кто дежурный"""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        answer_message = 'Что вы хотите получить?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Имя следующего дежурного', 'Список дежурных']
        keyboard.add(*buttons)
        types_message(message)
        # bot.send_message(copy_call.from_user.id, copy_call.message.text, reply_markup=keyboard)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, dej_step_2)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = existence(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


def dej_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    sheet_name = 'Дежурный'
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == 'Имя следующего дежурного':
            answer_message = Other_functions.File_processing.Working_with_a_file(sheet_name).next_dej()
            user_sticker = Other_functions.File_processing.Working_with_a_file(sheet_name).sticker_next_dej()
            # Пришлёт сообщение о дежурном
            types_message(message)
            bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
            if user_sticker is not None:
                # Пришлёт стикер этого дежурного
                bot.send_sticker(message.chat.id, user_sticker)
            print(f'{answer_bot}{answer_message}\n')
        elif message.text == 'Список дежурных':
            count_data_list = len(Other_functions.File_processing.Working_with_a_file(sheet_name).list_dej())
            answer_message = number_of_events(count_data_list)
            types_message(message)
            bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
            bot.register_next_step_handler(message, dej_step_3, sheet_name,
                                           count_data_list)  # Регистрация следующего действия
            print(f'{answer_bot}{answer_message}\n')
    except Exception as error:  # В любом другом случае бот сообщит об ошибке
        answer_message = 'Что-то пошло не так. Чтобы попробовать снова, жми /dezhurnyj'
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')
        print(str(error))
        logging_telegram_bot('error', str(error))


def dej_step_3(message, sheet_name, count_data_list):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    count = int(message.text)
    try:
        if count <= count_data_list:
            data_list = Other_functions.File_processing.Working_with_a_file(sheet_name).list_dej()
            Working_with_notifications.repeat_for_list(data_list, message.from_user.id, count)
        else:
            answer_message = f'Вы запрашиваете {count} записей, а есть только {count_data_list}.\n' \
                             f'Попробуйте снова - /dezhurnyj'
            types_message(message)
            bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
            print(f'{answer_bot}{answer_message}\n')
    except Exception as error:  # В любом другом случае бот сообщит об ошибке
        answer_message = 'Я не распознал число, попробуйте снова - /dezhurnyj'
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')
        print(str(error))
        logging_telegram_bot('error', str(error))


@bot.message_handler(commands=['get_list'])
def get_list(message):
    """Получить список всех пользователей"""

    if rights_admin(message) is True:
        answer_message = SQL().get_list_users()
        types_message(message)
        bot.reply_to(message, answer_message)
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['feed_back'])
def feed_back(message):
    """Обратная связь"""

    # if existence(message) is True:  # Проверка на наличие юзера в БД
    answer_message = 'Выберите тип обращения'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Что-то не работает', 'Есть идея новой функции', 'Другое']
    keyboard.add(*buttons)
    types_message(message)
    bot.reply_to(message, answer_message, reply_markup=keyboard)
    bot.register_next_step_handler(message, feed_back_step_2)  # Регистрация следующего действия
    print(f'{answer_bot}{answer_message}\n')
    # else:  # Если пользователь не зарегистрирован, бот предложит это сделать
    #     end_text = existence(message)
    #     types_message(message)
    #     bot.reply_to(message, end_text)
    #     print(f'{answer_bot}{end_text}\n')


def feed_back_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    text_answer = 'Опишите суть обращения. Чем подробнее тем лучше.\n'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Отмена']
    keyboard.add(*buttons)
    types_message(message)
    bot.reply_to(message, text_answer, reply_markup=keyboard)
    contacting_technical_support = f'{message.text}\n'
    bot.register_next_step_handler(message, feed_back_step_3,
                                   contacting_technical_support)  # Регистрация следующего действия
    print(f'{answer_bot}{text_answer}\n')


def feed_back_step_3(message, text_problem):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Обращение отменено.'
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')
    else:
        problem = f'FEED_BACK:\n{text_problem}{message.text}'
        logging_telegram_bot('info', problem)
        answer_message = f'Ваше обращение создано!\n' \
                         f'Тип: {text_problem}\n' \
                         f'Текст сообщения: {message.text}'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        bot.send_message(chat_id=Data.list_admins.get('Никита'),
                         text=f'Поступило новое обращение от пользователя:\n'
                              f'Тип: {text_problem}\n'
                              f'Текст сообщения: {message.text}')
        print(f'{answer_bot}{answer_message}\n')


@bot.message_handler(commands=['create_record'])
def create_record(message):
    """Создать уведомление"""

    if rights_admin(message) is True:
        answer_message = 'В какой лист добавить запись?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Уведомления для всех', 'Уведомления для подписчиков', 'Уведомления для админов', 'Отмена']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, create_record_step_2, buttons)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


def create_record_step_2(message, list_sheet):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Операция прервана.'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_message}\n')
    elif message.text not in list_sheet:
        answer_message = f'Нет листа с именем <{message.text}>! Необходимо выбрать из списка.'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Ок']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, create_record)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        list_of_answers = [message.text]
        answer_message = 'Введи текст уведомления'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        bot.register_next_step_handler(message, create_record_step_3,
                                       list_of_answers)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')


def create_record_step_3(message, list_of_answers):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    list_of_answers.append(message.text)
    answer_message = 'Введи дату когда уведомить о событии в формате <ДД.ММ.ГГГГ>.\n' \
                     '*Примечание: если дату указать некорректно, уведомление не сработает!*'
    types_message(message)
    bot.reply_to(message, answer_message)
    bot.register_next_step_handler(message, create_record_step_4, list_of_answers)  # Регистрация следующего действия
    print(f'{answer_bot}{answer_message}\n')


# noinspection PyTypeChecker
def create_record_step_4(message, list_of_answers):
    print(f'{full_name_user(message)} написал:\n{message.text}')

    list_of_answers.append(message.text)

    sheet_name = list_of_answers[0]
    date = list_of_answers[2]
    text_event = list_of_answers[1]

    answer_message = Other_functions.File_processing.Working_with_a_file(sheet_name).create_event(date, text_event)
    print(answer_message)
    types_message(message)
    bot.reply_to(message, answer_message)
    print(f'{answer_bot}{answer_message}\n')

    report_text = f'{full_name_user(message)} создал событие\n\n{answer_message}'
    bot.send_message(chat_id=Data.list_admins.get('Никита'), text=report_text)

    list_of_answers.clear()

    exit()


@bot.message_handler(commands=['games'])
def games(message):
    """Игры"""

    # if existence(message) is True:  # Проверка на наличие юзера в БД
    answer_message = 'На данный момент доступна одна игра'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Играть в "Угадаю число"', 'Отмена']
    keyboard.add(*buttons)
    types_message(message)
    bot.reply_to(message, answer_message, reply_markup=keyboard)
    bot.register_next_step_handler(message, games_step_2)  # Регистрация следующего действия
    print(f'{answer_bot}{answer_message}\n')
    # else:
    #     end_text = existence(message)
    #     types_message(message)
    #     bot.reply_to(message, end_text)
    #     print(f'{answer_bot}{end_text}\n')


def games_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    if message.text == 'Играть в "Угадаю число"':
        answer_message = 'Хорошо, начнём. Правила просты - загадай число от 1 до 100 а я попробую его угадать. ' \
                         'Я называю число, если твоё число меньше, жми "меньше", если твоё число больше, ' \
                         'жми "больше", а если угадал - "в точку".'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Начнём']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        print(f'{answer_bot}{answer_message}\n')
        bot.register_next_step_handler(message, games_step_3)
    elif message.text == 'Отмена':
        answer_message = 'Хорошо, сыграем в другой раз.'
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


def games_step_3(message):
    print(f'{full_name_user(message)} написал:\n{message.text}\n')
    if message.text == 'Начнём':
        number = random.randint(0, 100)
        answer_message = f'Возможно это {number}?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Больше', 'Меньше', 'В точку']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        print(f'{answer_message}')
        bot.register_next_step_handler(message, games_step_4, number, lower=1, high=100, count=1)


def games_step_4(message, number, lower, high, count):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Больше':
        print(f'{message.text}\n')
        lower = number + 1
    elif message.text == 'Меньше':
        print(f'{message.text}\n')
        high = number - 1
    elif message.text == 'В точку':
        print(f'{message.text}\n')
        answer_message = f'Я угадал твоё число за {count} ходов'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        text_message_2 = 'Сыграем ещё? /games'
        bot.send_message(message.from_user.id, text_message_2)
        print(f'{answer_message}\n{text_message_2}\n')
        exit()
    else:
        print(message.text)
    middle = (high + lower) // 2
    list_phrase = [
        'Я думаю твоё число',
        'Скорее всего это',
        'Всё, я знаю -',
        'Маловероятно, но похоже ты задумал число'
    ]
    random_phrase = random.choice(list_phrase)
    answer_message = f'{random_phrase} {middle}'
    print(answer_message)
    count += 1
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Больше', 'Меньше', 'В точку']
    keyboard.add(*buttons)
    types_message(message)
    bot.reply_to(message, answer_message, reply_markup=keyboard)
    bot.register_next_step_handler(message, games_step_4, middle, lower, high, count)


# @bot.message_handler(commands=['vote']) def vote(message): if existence(message) is True: json =
# Other_functions.Exchange_with_ERP({Data.number: message.from_user.id, Data.func_name4:
# '000000002'}).answer_from_ERP() if 'TEST_CODE' in json: test = json.get('TEST_CODE')
#
#             dict_answers = {}
#
#             output_json = {
#                 'TEST_CODE': {'ИдентификаторТемы': json.get('ИдентификаторТемы'),
#                               'Ответы': [dict_answers],
#                               'ИдентификаторПользователя': message.from_user.id}
#             }
#
#             for elem in test:
#                 # print(elem)
#                 id_question = elem.get('ИдентификаторВопроса')
#                 # print(id_question)
#                 text_question = elem.get('Вопрос')
#                 print(text_question)
#                 variable_question = elem.get('ВариантыОтветов')
#
#                 count = 1
#                 dict_id_answer = {}
#                 for variable in variable_question:
#                     id_answer = variable.get('ИдентификаторОтвета')
#                     text_variable_question = ' '.join(variable.get('Ответ').split())
#                     print(f'{count}. {text_variable_question}')
#                     dict_id_answer[count] = id_answer
#                     count += 1
#
#                 print()
#
#                 number_answer = int(input('Выберите один из вариантов ответа:\n'))
#                 if 0 < number_answer <= len(variable_question):
#                     answer = dict_id_answer[number_answer]  # Идентификатор ответа
#                     dict_answers[id_question] = answer
#                     dict_id_answer.clear()
#                 else:
#                     print('Ошибка')
#
#             print(output_json)
#         else:
#             print(json)
#     else:
#         answer_message = existence(message)
#         types_message(message)
#         bot.reply_to(message, answer_message)
#         print(f'{answer_bot}{answer_message}\n')


@bot.message_handler(commands=['defrosters'])
def check_defroster_step_1(message):
    """Подписка на мониторинг показаний дефростеров. Результат - придёт авто обновляемое сообщение."""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        if SQL().check_status_DB(message.from_user.id, 'def',
                                 'yes') is False:  # Если пользователь не наблюдатель
            answer_message = 'На данный момент вы не отслеживаете показания с датчиков дефростеров. Хотите начать?'
        else:
            answer_message = 'На данный момент вы являетесь наблюдателем показаний с датчиков дефростеров. Прекратить' \
                             ' отслеживать? '
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Да', 'Отмена']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, check_defroster_step_2)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


def check_defroster_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Да':
        SQL().change_status_DB(message.from_user.id, 'def')  # Изменить текущий статус
        answer_message = 'Подождите...'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_message}\n')
        time.sleep(3)

        if SQL().check_status_DB(message.from_user.id, 'def',
                                 'yes') is True:  # Если пользователь наблюдатель
            SQL().add_user_by_table(message.from_user.id, 'def', 'yes', 'tracking_sensor_defroster')

            message_id = bot.send_message(message.from_user.id, 'Start tracking sensor in defroster').message_id
            SQL().update_mess_id_by_table(message.from_user.id, message_id, 'tracking_sensor_defroster',
                                          'def')
            bot.pin_chat_message(message.from_user.id, message_id=message_id)  # Закрепляет сообщение у пользователя

            end_message = 'Теперь вам доступны показания датчиков дефростеров. Сообщение обновляется автоматически.'
            bot.send_message(chat_id=Data.list_admins.get('Никита'),
                             text=f'{full_name_user(message)} начал отслеживать показания датчиков дефростеров.')

            types_message(message)
            bot.send_message(chat_id=message.from_user.id, text=end_message)
            print(f'{answer_bot}{end_message}\n')
        else:
            if SQL().check_for_existence(message.from_user.id, 'tracking_sensor_defroster') is False:
                pass
            else:
                if SQL().get_mess_id(message.from_user.id) is not None:
                    message_id = SQL().get_mess_id(message.from_user.id)

                    Data.bot.unpin_chat_message(chat_id=message.from_user.id, message_id=message_id)
                    Data.bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

                SQL().log_out(message.from_user.id, 'tracking_sensor_defroster')

                end_message = 'Вы прекратили отслеживать показания. Если передумаете клик - /defrosters.'
                bot.send_message(chat_id=Data.list_admins.get('Никита'),
                                 text=f'{full_name_user(message)} прекратил отслеживать показания датчиков '
                                      f'дефростеров.')

                types_message(message)
                bot.send_message(chat_id=message.from_user.id, text=end_message)
                print(f'{answer_bot}{end_message}\n')
    elif message.text == 'Отмена':
        end_text = 'Операция прервана'
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['all_sensors'])
def check_error_sensor(message):
    if rights_admin(message) is True:  # Проверка на наличие юзера в БД и является ли он админом
        # Если пользователь не наблюдатель
        if SQL().check_status_DB(message.from_user.id, 'observer_all_sensor', 'yes') is False:
            answer_message = 'На данный момент вы не отслеживаете неисправные датчики. Хотите начать?'
        else:
            answer_message = 'На данный момент вы отслеживаете неисправные датчики. Прекратить отслеживать?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Да', 'Отмена']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, check_error_sensor_step_2)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


def check_error_sensor_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Да':
        SQL().change_status_DB(message.from_user.id, 'observer_all_sensor')  # Изменить текущий статус
        answer_message = 'Подождите...'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_message}\n')
        time.sleep(3)

        if SQL().check_status_DB(message.from_user.id, 'observer_all_sensor',
                                 'yes') is True:  # Если пользователь наблюдатель
            SQL().add_user_by_table(message.from_user.id, 'observer_all_sensor', 'yes',
                                    'observers_for_faulty_sensors')

            message_id = bot.send_message(message.from_user.id, 'Start tracking error sensors').message_id
            SQL().update_mess_id_by_table(message.from_user.id, message_id,
                                          'observers_for_faulty_sensors',
                                          'observer_all_sensor')
            bot.pin_chat_message(message.from_user.id, message_id=message_id)  # Закрепляет сообщение у пользователя

            end_message = 'Теперь вам доступен список неисправных датчиков. Сообщение обновляется автоматически.'
            bot.send_message(chat_id=Data.list_admins.get('Никита'),
                             text=f'{full_name_user(message)} начал отслеживать список неисправных датчиков.')

            types_message(message)
            bot.send_message(chat_id=message.from_user.id, text=end_message)
            print(f'{answer_bot}{end_message}\n')
        else:
            if SQL().check_for_existence(message.from_user.id, 'observers_for_faulty_sensors') is False:
                pass
            else:
                if SQL().get_mess_id(message.from_user.id) is not None:
                    message_id = SQL().get_mess_id(message.from_user.id)

                    Data.bot.unpin_chat_message(chat_id=message.from_user.id, message_id=message_id)
                    Data.bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

                SQL().log_out(message.from_user.id, 'observers_for_faulty_sensors')

                end_message = 'Вы прекратили отслеживать список неисправных датчиков. ' \
                              'Если передумаете клик - /all_sensors.'
                bot.send_message(chat_id=Data.list_admins.get('Никита'),
                                 text=f'{full_name_user(message)} прекратил отслеживать список неисправных датчиков.')

                types_message(message)
                bot.send_message(chat_id=message.from_user.id, text=end_message)
                print(f'{answer_bot}{end_message}\n')
    elif message.text == 'Отмена':
        end_text = ''
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


@bot.message_handler(commands=['answer'])
def answer(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    if message.from_user.id == Data.list_admins.get('Никита'):
        if SQL().count_not_answer() > 0:
            answer_message = SQL().search_not_answer()
            message_bot = f'Как ответить на это сообщение?\n<{answer_message}>'
            bot.reply_to(message, message_bot)
            bot.register_next_step_handler(message, answer_step_two, answer_message)
        else:
            message_bot = SQL().search_not_answer()
            bot.reply_to(message, message_bot)
        print(f'{answer_bot}{message_bot}\n')


def answer_step_two(message, question):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    text_answer = message.text
    SQL().update_answer_speak_DB(question, text_answer)

    message_bot = 'Запомнил. Продолжим? /answer'
    bot.reply_to(message, message_bot)
    print(f'{answer_bot}{message_bot}\n')


@bot.message_handler(commands=['vacation'])
def get_number_vacation_days(message):
    """Функция возвращает кол-во накопившихся дней отпуска либо текст с описанием при возникновении ошибки."""

    if existence(message) is True:
        count_day = Exchange_with_ERP.Exchange_with_ERP.Exchange_with_ERP(
            {Data.number: message.from_user.id}).answer_from_ERP()
        if isinstance(count_day, int):
            days = declension_day(count_day)
            answer_message = f'На данный момент у вас накоплено ||{count_day} {days}|| отпуска'
            types_message(message)
            bot.send_message(chat_id=message.from_user.id, text=answer_message, parse_mode='MarkdownV2')
            print(f'{answer_bot}На данный момент у вас накоплено &&& дней отпуска\n')
            logging_telegram_bot('info',
                                 f'Пользователь {message.from_user.first_name}({message.from_user.id}) '
                                 f'получил ответ от ERP по кол-ву накопленных дней отпуска.')
        else:
            answer_message = str(count_day)  # Тут текст ошибки
            types_message(message)
            bot.send_message(chat_id=message.from_user.id, text=answer_message)
            print(f'{answer_bot}{answer_message}\n')
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


@bot.message_handler(commands=['verification'])
def verification(message):
    """Предлагает пользователю обновить ID Telegram в 1С с указанным ИНН. Либо возвращает str(ошибку)."""

    if SQL().check_for_existence(message.from_user.id) is True:  # Проверка на наличие юзера в БД
        SQL().update_data_user(message)
        answer_message = 'Для верификации необходим номер вашего ИНН (физ. лицо). ' \
                         'Эти данные нужны для проверки личности пользователя в 1С. ' \
                         'Если вы готовы предоставить их прямо сейчас - нажмите "Ок"'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Ок', 'Отмена']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, verification_step_2)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


def verification_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Ок':
        answer_message = 'Введите номер вашего ИНН'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        bot.register_next_step_handler(message, verification_step_3)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    elif message.text == 'Отмена':
        end_text = 'Операция прервана. Когда будете готовы клик -> /verification'
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')
        exit()


def verification_step_3(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    if len(message.text) == 12:
        answer_message = Exchange_with_ERP.Exchange_with_ERP.Exchange_with_ERP(
            {Data.number: message.from_user.id, Data.verification: message.text}).answer_from_ERP()
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')
        logging_telegram_bot('info',
                             f'Пользователь {message.from_user.first_name}({message.from_user.id}) '
                             f'получил ответ от ERP по верификации.')
        SQL().update_sqlite_table('yes', message.from_user.id, 'verify_erp')
    else:
        error_text = 'Не удалось выполнить запрос. Номер ИНН должен состоять из 12 символов и содержать ' \
                     'только цифры. Проверьте корректно ли вы указали данные. Попробуйте снова -> /verification'
        bot.reply_to(message, error_text)
        print(f'{answer_bot}{error_text}\n')


@bot.message_handler(content_types=['text'])
def speak(message):
    # if existence(message) is True:
    text_message_user = message.text.capitalize()
    the_answer_to_the_question = SQL().talk(text_message_user)
    if the_answer_to_the_question is None:
        text_one = random.choice(Data.list_answer_speak)
        text_two = '\nГоворите со мной чаще, я научусь!'
        end_text = f'{text_one} {text_two}'
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')

        count = SQL().count_not_answer()
        end_message = f'На данный момент есть {count} вопросов без ответа. Ответить на вопросы - /answer'
        bot.send_message(chat_id=Data.list_admins.get('Никита'), text=end_message)
    else:
        types_message(message)
        bot.reply_to(message, the_answer_to_the_question)
        print(f'{answer_bot}{the_answer_to_the_question}\n')
        # bot.send_message(message.from_user.id, answer)


# else:
#     answer_message = existence(message)
#     types_message(message)
#     bot.reply_to(message, answer_message)
#     print(f'{answer_bot}{answer_message}\n')


if __name__ == '__main__':
    while True:
        try:
            text_message = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nTelegram_bot.py начал работу'
            Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_message)
            print(text_message)
            bot.polling(none_stop=True)
        # except telebot.ReadTimeout:
        #     time.sleep(3)
        #     text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nПревышено время ожидания запроса'
        #     bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text)
        #     print(str(text))
        #     logging_telegram_bot('error', str(text))
        # except KeyboardInterrupt:
        #     print(sys.stderr, '\nExiting by user request\n')
        #     bot.stop_polling()
        #     sys.exit(0)
        #     break
        except Exception as e:
            time.sleep(3)
            text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nВ Telegram_bot.py возникла ошибка: {e} '
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text)
            print(str(e))
            logging_telegram_bot('error', str(e))
            # os.kill(os.getpid(), 9)

