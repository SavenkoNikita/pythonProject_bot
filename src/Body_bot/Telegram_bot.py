import datetime as datetime
import random
import time

import requests
import telebot

import Data
import src.Other_functions.Working_with_notifications
from src.Exchange_with_ERP.Exchange_with_ERP import Exchange_with_ERP
from src.Other_functions import Working_with_notifications
from src.Other_functions.File_processing import Working_with_a_file
from src.Other_functions.Functions import SQL, can_help, logging_telegram_bot, number_of_events, declension_day, \
    string_to_dict
from src.Other_functions.Working_with_notifications import Notification
from src.Other_functions.Functions import Decorators

# from poetry.layouts import src

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
        SQL().update_data_user(user_id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username)
        return True
        # if SQL().check_verify_in_ERP(user_id) is True:
        #     return True
        # else:
        #     verify_error = 'Чтобы воспользоваться функцией необходимо пройти верификацию в 1С -> /verification'
        #     print(f'{answer_bot}{verify_error}\n')
        #     return verify_error
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

    count_text_message = random.randint(1, 3)  # Случайное кол-во секунд будет имитироваться набор текста
    # count_text_message = float(int(0.1))

    bot.send_chat_action(user_id, action='typing')
    time.sleep(count_text_message)


# @bot.message_handler(commands=['test'])
# def test(message):
#     print(message)
#     # if bot.message_handler(commands='dezhurnyj'):
#     #     Bot_commands(message).command_dezhurnyj()

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
        # bot.send_message(chat_id=message.from_user.id,
        #                  text='Подождите. Сохраняю данные о вас...')
        # time.sleep(5)  # Подождать указанное кол-во секунд
        bot.send_message(chat_id=message.from_user.id,
                         text='Регистрация выполнена успешно!')
        register_message = f'Добро пожаловать {message.from_user.first_name}!\n\n' \
                           f'Вот самые популярные функции:\n' \
                           f'• Чтобы подписаться на барахолку нажмите сюда -> /baraholka и следуйте инструкции\n' \
                           f'• Для того чтобы быть в курсе о дежурном из IT-отдела в ближайшие выходные, ' \
                           f'необходимо подписаться на уведомления -> /subscribe\n' \
                           f'• Узнать количество накопившихся дней отпуска -> /vacation\n\n' \
                           f'Со списком команд можно ознакомиться открыв меню, расположенное слева от ' \
                           f'поля ввода текста, или получить полный, доступный вам список тут -> /help\n'
        # f'Остался последний шаг. Необходимо пройти верификацию в 1С. ' \
        # f'Для этого нажмите сюда -> /verification.'
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


@bot.message_handler(commands=['help'])  # , func=help_command)
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
    # bot.send_message(message.from_user.id, text='Главное меню', reply_markup=Menu_bot.Bot_menu().main_menu())


@bot.message_handler(commands=['invent'])
def invent(message):
    """Узнать кто следующий на инвентаризацию"""

    list_name = 'Инвентаризация'  # Имя страницы

    if rights_admin(message) is True:
        if Working_with_a_file(list_name).read_file() is not None:
            answer_message = Working_with_a_file(list_name).next_invent()
            sticker = Working_with_a_file(list_name).sticker_next_dej()
            types_message(message)
            bot.reply_to(message, answer_message)
            if sticker is not None:
                bot.send_sticker(message.chat.id, sticker)
            print(f'{answer_bot}{answer_message}\n')
        else:
            answer_message = Working_with_a_file(list_name).next_invent()
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
            end_text = 'Подписка на уведомления активирована. Теперь вам будут приходить уведомления о том, ' \
                       'кто из системных администраторов дежурит в ближайшие выходные или праздничные дни, ' \
                       'кто в отпуске и прочая информация.\n\n' \
                       '#####\n' \
                       'В эту подписку не входят уведомления из барахолки! Внимательно ознакомьтесь со списком ' \
                       'доступных команд -> /help\n' \
                       '#####\n\n' \
                       'Чтобы отказаться от рассылки, жми /unsubscribe '
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


@bot.message_handler(commands=['dezhurnyj'])  # , func=command_dezhurnyj)
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
            answer_message = Working_with_a_file(sheet_name).next_dej()
            user_sticker = Working_with_a_file(sheet_name).sticker_next_dej()
            # Пришлёт сообщение о дежурном
            types_message(message)
            bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
            if user_sticker is not None:
                # Пришлёт стикер этого дежурного
                bot.send_sticker(message.chat.id, user_sticker)
            print(f'{answer_bot}{answer_message}\n')
        elif message.text == 'Список дежурных':
            count_data_list = len(Working_with_a_file(sheet_name).list_dej())
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
            data_list = Working_with_a_file(sheet_name).list_dej()
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
    buttons = ['Что-то не работает', 'Есть идея новой функции', 'Другое', 'Отмена']
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
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Обращение отменено.'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_message}\n')
    else:
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
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
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

    answer_message = Working_with_a_file(sheet_name).create_event(date, text_event)
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
        # text_message_2 = 'Сыграем ещё? /games'
        # bot.send_message(message.from_user.id, text_message_2)
        # print(f'{answer_message}\n{text_message_2}\n')
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
                                 'yes') is True:  # Если пользователь не наблюдатель
            SQL().add_user_by_table(message.from_user.id, 'def', 'yes', 'tracking_sensor_defroster')

            message_id = bot.send_message(message.from_user.id, 'Через некоторое время, на месте этого сообщения, '
                                                                'появятся показания датчиков').message_id
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
    # if rights_admin(message) is True:  # Проверка на наличие юзера в БД и является ли он админом
    #     Если пользователь не наблюдатель
    if SQL().check_status_DB(message.from_user.id, 'observer_all_sensor', 'yes') is False:
        answer_message = 'Инструмент позволяет отслеживать неисправные термодатчики. Вам придёт автообновляемое ' \
                         'сообщение со списком. А так же будут поступать сообщения как только обнаружится ' \
                         'неисправность. На данный момент вы не подписаны на уведомления. Хотите начать?\n' \
                         '*** выберите действие ниже ***'
    else:
        answer_message = 'На данный момент вы подписаны на уведомления о неисправных датчиках. ' \
                         'Прекратить отслеживать?\n' \
                         '*** выберите действие ниже ***'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Да', 'Отмена']
    keyboard.add(*buttons)
    types_message(message)
    bot.reply_to(message, answer_message, reply_markup=keyboard)
    bot.register_next_step_handler(message, check_error_sensor_step_2)  # Регистрация следующего действия
    print(f'{answer_bot}{answer_message}\n')
    # else:
    #     answer_message = existence(message)
    #     types_message(message)
    #     bot.reply_to(message, answer_message)
    #     print(f'{answer_bot}{answer_message}\n')


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
        if SQL().check_verify_in_ERP(message.from_user.id) is True:
            count_day = Exchange_with_ERP({Data.number: message.from_user.id}).answer_from_ERP()
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
            verify_error = 'Чтобы воспользоваться функцией необходимо пройти верификацию в 1С -> /verification'
            types_message(message)
            bot.send_message(chat_id=message.from_user.id, text=verify_error)
            print(f'{answer_bot}{verify_error}\n')
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


@bot.message_handler(commands=['verification'])
def verification(message):
    """Предлагает пользователю обновить ID Telegram в 1С с указанным ИНН. Либо возвращает str(ошибку)."""

    if SQL().check_for_existence(message.from_user.id) is True:  # Проверка на наличие юзера в БД
        SQL().update_data_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username)
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
        # exit()


def verification_step_3(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    if len(message.text) == 12:
        answer_message = Exchange_with_ERP(
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


@bot.message_handler(commands=['baraholka'])
def baraholka(message):
    user_id = message.from_user.id
    if existence(message) is True:
        status = ''
        if SQL().check_status_bar(user_id) is True:
            status = 'вы подписаны на уведомления!'
        elif SQL().check_status_bar(user_id) is False:
            status = 'вы не подписаны на уведомления\n' \
                     'Как только вы активируете подписку, вам будут присланы все те лоты которые ещё не забрали.\n' \
                     'Не пугайтесь, их может быть много!\n' \
                     'Чтобы понять как работает барахолка, настоятельно рекомендуем ознакомиться с описанием!'

        text_to_user = f'Давно не виделись {message.from_user.first_name}! В данный момент {status}'
        bot.reply_to(message, text=text_to_user)
        print(f'{answer_bot}{text_to_user}\n')
        time.sleep(3)
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Изменить статус', 'Оставить как есть']
        manual = ['Как это работает?']
        keyboard.add(*buttons)
        keyboard.add(*manual)
        types_message(message)
        text_to_user = 'Выберите действие:'
        bot.send_message(chat_id=user_id,
                         text=text_to_user,
                         reply_markup=keyboard)
        print(f'{answer_bot}{text_to_user}\n')
        bot.register_next_step_handler(message, baraholka_step_2)
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


def baraholka_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Изменить статус':
        answer_SQL = SQL().change_status_bar(message.from_user.id)
        text_to_user = 'Статус успешно изменён!'
        bot.send_message(chat_id=message.from_user.id,
                         text=f'{text_to_user}\n{answer_SQL}',
                         reply_markup=hide_keyboard)
        print(f'{answer_bot}{text_to_user}\n')
    elif message.text == 'Оставить как есть':
        text_to_user = 'Хорошо. До новых сообщений! ;)'
        bot.send_message(chat_id=message.from_user.id,
                         text=text_to_user,
                         reply_markup=hide_keyboard)
        print(f'{answer_bot}{text_to_user}\n')
    elif message.text == 'Как это работает?':
        manual = 'IT - отдел периодически списывает оборудование и комплектующие. С помощью барахолки мы ' \
                 'реализовали возможность выдавать это на руки тем, кто в них заинтересован.\n' \
                 'Каждое такое списание будет выглядеть здесь в виде постов.\n' \
                 'Такие сообщения будут содержать кнопки управления:\n' \
                 '• "Забронировать". Из названия понятно что она делает, но есть нюансы. Кто окажется самым ' \
                 'быстрым на диком западе, тот и забронирует лот. Для всех остальных он станет недоступным для ' \
                 'бронирования на сутки, либо пока пользователь не отменит бронь, а если заберёт его, то кто ' \
                 'успел тот и съел. Помимо этого, каждый пользователь может бронировать не более 3х лотов ' \
                 'одновременно!\n' \
                 '• "Отменить бронь". Если вы всё же успели забронировать лот, но по какой-то причине ' \
                 'передумали его забирать, эта кнопка вернёт остальным подписчикам возможность забронировать ' \
                 'лот для себя. Напомним, бронь сохраняется за вами не более суток!\n' \
                 '• "Лот уже у меня". Эта кнопка подтверждает, что лот находится у вас на руках, а так же все ' \
                 'подписчики увидят, что он более не доступен.\n\n' \
                 'Все лоты можно получить в IT - отделе, при условии, что они забронированы вами. Некоторые ценные ' \
                 'лоты могут быть платными, но цена, как правило символичная.\n' \
                 'Если готовы приступить нажмите сюда -> /baraholka и далее на кнопку "Изменить статус"'

        bot.send_message(chat_id=message.from_user.id,
                         text=manual,
                         reply_markup=hide_keyboard)

        print(f'{answer_bot}{manual}\n')


@bot.message_handler(commands=['place_a_lot'])
def place_a_lot(message):
    user_id = message.from_user.id
    if rights_admin(message) is True:
        text_answer = 'Для создания лота, необходимо\n' \
                      '• Дать ему название\n' \
                      '• Прикрепить фото\n' \
                      '• Краткое описание\n\n' \
                      '*Выбери действие*'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Создать лот', 'Возможно позже']
        keyboard.add(*buttons)
        types_message(message)
        bot.send_message(chat_id=user_id, text=text_answer, reply_markup=keyboard)
        print(f'{answer_bot}{text_answer}\n')
        bot.register_next_step_handler(message, place_a_lot_step_2)
    else:
        answer_message = existence(message)
        types_message(message)
        bot.reply_to(message, answer_message)
        print(f'{answer_bot}{answer_message}\n')


def place_a_lot_step_2(message):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    user_id = message.from_user.id
    name_lot = None
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Создать лот':
        answer_text = 'Как будет называться лот?'
        bot.send_message(chat_id=user_id, text=answer_text, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot_step_3, name_lot)
    elif message.text == 'Возможно позже':
        answer_text = 'Создание лота отменено.'
        bot.send_message(chat_id=user_id, text=answer_text, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_text}\n')


def place_a_lot_step_3(message, name_lot):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    user_id = message.from_user.id
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if name_lot is None:
        name_lot = message.text
    else:
        name_lot = name_lot

    answer_text = 'Теперь отправь мне фотографию лота.\n' \
                  '*Примечание: при отправке нескольких фото, будет использоваться первая прикреплённая!'

    bot.send_message(chat_id=user_id,
                     text=answer_text,
                     reply_markup=hide_keyboard)
    print(f'{answer_bot}{answer_text}\n')
    bot.register_next_step_handler(message, place_a_lot_step_4, name_lot)


def place_a_lot_step_4(message, name_lot):
    # name_lot = name_lot
    # print(message)
    if message.photo is not None:
        print(f'{full_name_user(message)} прикрепил фото.')
        photo_id = message.photo[0].file_id

        answer_text = 'Теперь нужно добавить описание к лоту (что это, рабочее ли состояние, возможные дефекты)'

        bot.send_message(message.chat.id, text=answer_text)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot_step_5, name_lot, photo_id)
    else:
        print(f'{full_name_user(message)} прикрепил не фото а что-то другое.')
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Ещё попытка']
        keyboard.add(*buttons)
        types_message(message)

        answer_text = 'Не спеши! На данном этапе мне нужна фотография. Попробуем ещё раз. Нажми на кнопку ниже'

        bot.send_message(message.chat.id,
                         text=answer_text,
                         reply_markup=keyboard)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot_step_3, name_lot)


def place_a_lot_step_5(message, name_lot, photo_id):
    print(f'{full_name_user(message)} прикрепил фото.')
    user_id = message.from_user.id
    description_lot = message.text

    answer_text = 'Указать стоимость лота?\n' \
                  '*Выберите действие*'

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Указать цену', 'Бесплатно']
    keyboard.add(*buttons)
    types_message(message)
    bot.send_message(chat_id=user_id, text=answer_text, reply_markup=keyboard)

    print(f'{answer_bot}{answer_text}\n')
    bot.register_next_step_handler(message, place_a_lot_step_6, name_lot, photo_id, description_lot)


def place_a_lot_step_6(message, name_lot, photo_id, description_lot):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    user_id = message.from_user.id

    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Указать цену':
        answer_text = 'Сколько будет стоить лот?'
        bot.send_message(chat_id=user_id, text=answer_text, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot_step_7, name_lot, photo_id, description_lot)
    elif message.text == 'Бесплатно':
        # answer_text = 'Записано'
        # bot.send_message(chat_id=user_id, text=answer_text, reply_markup=hide_keyboard)
        # print(f'{answer_bot}{answer_text}\n')
        price = "бесплатно"

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Продолжить']
        keyboard.add(*buttons)
        types_message(message)

        answer_text = 'Для того чтобы продолжить нажмите кнопку ниже'

        bot.send_message(message.chat.id, text=answer_text, reply_markup=keyboard)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot_step_8, name_lot, photo_id, description_lot, price)


def place_a_lot_step_7(message, name_lot, photo_id, description_lot):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    price = f'{message.text}₽'
    if message.text is not None:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Продолжить']
        keyboard.add(*buttons)
        types_message(message)

        answer_text = 'Для того чтобы продолжить нажмите кнопку ниже'

        bot.send_message(message.chat.id, text=answer_text, reply_markup=keyboard)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot_step_8, name_lot, photo_id, description_lot, price)
    else:
        answer_text = "Кажется вы забыли указать цену! Укажите её прямо сейчас:"
        bot.reply_to(text=answer_text)
        bot.register_next_step_handler(message, place_a_lot_step_7, name_lot, photo_id, description_lot)


def place_a_lot_step_8(message, name_lot, photo_id, description_lot, price):
    lot_number = Working_with_notifications.Notification().get_last_record_lots() + 1
    # name_lot = name_lot
    # photo_id = photo_id
    # description_lot = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Разместить', 'Создать заново', 'Удалить пост']
    keyboard.add(*buttons)
    types_message(message)

    answer_text = 'Вот так пользователи будут видеть созданный лот:\n' \
                  '*Выбери действие*'

    bot.send_message(message.chat.id, text=answer_text, reply_markup=keyboard)
    print(f'{answer_bot}{answer_text}\n')
    bot.send_photo(message.chat.id,
                   caption=f'Лот №{lot_number}\n\n'
                           f'Название: {name_lot}\n\n'
                           f'Описание: {description_lot}\n\n'
                           f'Стоимость: {price}\n\n',
                   photo=photo_id)
    bot.register_next_step_handler(message, place_a_lot_step_9, name_lot, photo_id, description_lot, price)


def place_a_lot_step_9(message, name_lot, photo_id, description_lot, price):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    user_id = message.from_user.id
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Разместить':
        SQL().record_lot_to_DB(name_lot, photo_id, description_lot)  # Помещаем имя, id фото и описание в БД
        Notification().notification_for_subs_lots(name_lot, photo_id, description_lot, price)  # Рассылка подписчикам
        id_callback_data = Notification().get_last_record_lots()  # Получаем id последнего лота из БД
        keyboard = telebot.types.InlineKeyboardMarkup()  # Инициализация клавиатуры
        button = telebot.types.InlineKeyboardButton(text='Забронировать лот', callback_data=id_callback_data)
        keyboard.add(button)

        answer_text = 'Лот успешно разослан подписчикам барахолки!'

        bot.send_message(chat_id=user_id,
                         text=answer_text,
                         reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_text}\n')
        # bot.answer_callback_query(chat_id=user_id,
        #                           text='Лот успешно разослан подписчикам барахолки!',
        #                           reply_markup=hide_keyboard)
    elif message.text == 'Создать заново':
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Начать']
        keyboard.add(*buttons)
        types_message(message)

        answer_text = 'Для того чтобы продолжить нажмите кнопку ниже'

        bot.send_message(message.chat.id, text=answer_text, reply_markup=keyboard)
        print(f'{answer_bot}{answer_text}\n')
        bot.register_next_step_handler(message, place_a_lot)
    elif message.text == 'Удалить пост':
        answer_text = 'Публикация поста отменена'
        bot.send_message(chat_id=user_id, text=answer_text, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_text}\n')


@bot.message_handler(commands=['urgent_message'])
def urgent_message(message):
    if rights_admin(message) is True:
        answer_message = 'Кому вы собираетесь разослать сообщение?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Всем пользователям', 'Подписчикам', 'Админам', 'Барахольщикам', 'Отмена']
        keyboard.add(*buttons)
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=keyboard)
        bot.register_next_step_handler(message, urgent_message_step_2, buttons)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')
    else:
        end_text = rights_admin(message)
        types_message(message)
        bot.reply_to(message, end_text)
        print(f'{answer_bot}{end_text}\n')


def urgent_message_step_2(message, list_sheet):
    print(f'{full_name_user(message)} написал:\n{message.text}')
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Операция прервана.'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_message}\n')
    elif message.text not in list_sheet:
        answer_message = f'<{message.text}> не подходит.. Необходимо выбрать из списка!'
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
        bot.register_next_step_handler(message, urgent_message_step_3,
                                       list_of_answers)  # Регистрация следующего действия
        print(f'{answer_bot}{answer_message}\n')


def urgent_message_step_3(message, list_of_answers):
    print(f'{full_name_user(message)} написал:\n{message.text}')

    list_of_answers.append(message.text)

    sheet_name = list_of_answers[0]
    text_event = list_of_answers[1]

    if sheet_name == 'Всем пользователям':
        end_message = f'• Уведомление для зарегистрированных пользователей •\n\n' \
                      f'{text_event}'
    elif sheet_name == 'Подписчикам':
        end_message = f'• Уведомление для подписчиков •\n\n' \
                      f'{text_event}'
    elif sheet_name == 'Админам':
        end_message = f'• Уведомление для администраторов •\n\n' \
                      f'{text_event}'
    elif sheet_name == 'Барахольщикам':
        end_message = f'• Уведомление для подписчиков барахолки •\n\n' \
                      f'{text_event}'
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()  # Вызов кнопки
        keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
        error_message = 'Что-то пошло не так. Обратитесь к разработчику.'
        types_message(message)
        bot.reply_to(message, error_message, reply_markup=keyboard)

    confirm_message = f'Уведомление будет выглядеть вот так: \n•••••\n' \
                      f'{end_message}\n•••••\n' \
                      f'Отправить его?\n' \
                      f'*Выберите действие*'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Да', 'Отмена']
    keyboard.add(*buttons)
    types_message(message)
    bot.reply_to(message, confirm_message, reply_markup=keyboard)
    bot.register_next_step_handler(message, urgent_message_step_4, list_of_answers)  # Регистрация следующего действия
    print(f'{answer_bot}{confirm_message}\n')


def urgent_message_step_4(message, list_of_answers):
    print(f'{full_name_user(message)} написал:\n{message.text}')

    sheet_name = list_of_answers[0]
    text_event = list_of_answers[1]

    if message.text == 'Да':
        if sheet_name == 'Всем пользователям':
            end_message = f'• Уведомление для зарегистрированных пользователей •\n\n' \
                          f'{text_event}'
            src.Other_functions.Working_with_notifications.Notification().send_a_notification_to_all_users(end_message)
        elif sheet_name == 'Подписчикам':
            end_message = f'• Уведомление для подписчиков •\n\n' \
                          f'{text_event}'
            src.Other_functions.Working_with_notifications.Notification().send_notification_to_subscribers(end_message)
        elif sheet_name == 'Админам':
            end_message = f'• Уведомление для администраторов •\n\n' \
                          f'{text_event}'
            src.Other_functions.Working_with_notifications.Notification().send_notification_to_administrators(
                end_message)
        elif sheet_name == 'Барахольщикам':
            end_message = f'• Уведомление для подписчиков барахолки •\n\n' \
                          f'{text_event}'
            src.Other_functions.Working_with_notifications.Notification().notification_for_sub_baraholka(end_message)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()  # Вызов кнопки
            keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
            error_message = 'Что-то пошло не так. Обратитесь к разработчику.'
            types_message(message)
            bot.reply_to(message, error_message, reply_markup=keyboard)
    elif message.text == 'Отмена':
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        answer_message = 'Операция прервана.'
        types_message(message)
        bot.reply_to(message, answer_message, reply_markup=hide_keyboard)
        print(f'{answer_bot}{answer_message}\n')

    exit()


@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    user_id = c.from_user.id  # Получаем user_id
    user_name = c.from_user.first_name  # Получаем имя пользователя
    dict_data = string_to_dict(c.data)  # Получаем dict(словарь) из входных данных
    key = [key for key in dict_data.keys()][0]  # Достаём ключ из словаря
    number_lot = dict_data.get(key)  # Достаём значение из словаря

    SQL().collect_statistical_information(user_id)

    if key == 'lot':
        answer_sql = SQL().booked_lots(number_lot, user_id)  # Попытка юзером забронировать лот
        if answer_sql != 'Success':  # Если лот забронирован
            bot.answer_callback_query(c.id, text=answer_sql)  # Вызывает у юзера всплывающее окно с текстом ошибки
        elif answer_sql == 'Success':  # Если лот не забронирован
            count_booked_lot = SQL().count_booked_lot(user_id)
            answer_text = f'Использовано {count_booked_lot} из 3 броней'
            bot.answer_callback_query(c.id, text=answer_text)
            # SQL().edit_message_lots(number_lot)  # Пользователь бронирует лот за собой и у всех подписчиков в этом
            SQL().booked_lots(number_lot, user_id)
            print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                  f'Пользователь {user_name} забронировал лот №{number_lot}.\n'
                  f'Осталось доступных броней - {3 - count_booked_lot}.\n')
    elif key == 'cancel':
        SQL().cancel_lot(number_lot)  # Пользователь отменяет бронь на лот
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
              f'Пользователь {user_name} отменил бронь на лот №{number_lot}.\n')
    elif key == 'sold':
        SQL().sold_lot(id_lot=number_lot, user_id=user_id)  # Пользователь подтверждает что забрал лот
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
              f'Пользователь {user_name} подтвердил, что забрал лот №{number_lot}.\n')
    elif key == 'confirm':
        SQL().confirm_the_issue(id_lot=number_lot)  # Админ подтверждает выдачу
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
              f'Администратор {user_name} подтвердил выдачу лота №{number_lot}.\n')
    elif key == 'refute':
        SQL().refute_the_issue(id_lot=number_lot)  # Админ опровергает выдачу
        print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
              f'Администратор {user_name} опроверг выдачу лота №{number_lot}.\n')


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

# @bot.message_handler(content_types=['photo'])
# def get_id_photo(message):
#     photo_id = message.photo[0].file_id
#     answer_message = f'photo_id изображения - {photo_id}'
#     bot.reply_to(message, text=answer_message)


if __name__ == '__main__':
    while True:
        try:
            text_message = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n' \
                           f'Telegram_bot.py начал работу'
            # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_message)
            print(text_message)
            bot.polling(none_stop=True)
            # bot.polling()
        except KeyboardInterrupt:
            print('job stop with keyboard')
            bot.stop_polling()
            # bot.stop_bot()
        except requests.exceptions.ReadTimeout:
            time.sleep(3)
            text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n' \
                   f'Превышено время ожидания запроса'
            # bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text)
            print(text)
            logging_telegram_bot('error', text)
        except requests.ConnectionError:
            print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                  f'Нет соединения с сервером')
            time.sleep(60)
            print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                  f'Попытка соединения')
        except BaseException:
            print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                  f'Возникла ошибка типа передаваемых данных')
        except Exception as e:
            time.sleep(3)
            text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n' \
                   f'В Telegram_bot.py возникла ошибка: {e} '
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text)
            print(str(e))
            logging_telegram_bot('error', str(e))
