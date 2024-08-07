import datetime as datetime
import inspect
import random
import time
from pprint import pprint

import requests
import telebot

import src.Other_functions.Functions
from src.Body_bot import Secret
from src.Other_functions import Decorators
from src.Other_functions import Working_with_notifications, ERP
from src.Other_functions.File_processing import Working_with_a_file
from src.Other_functions.Functions import SQL, can_help, logging_telegram_bot, number_of_events, declension_day, \
    string_to_dict, declension
from src.Other_functions.Working_with_notifications import Notification

time_now = lambda x: time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(x))  # Конвертация даты в читабельный вид
bot = Secret.bot
dev_id = Secret.list_admins.get('Никита')


def answer_bot(message, text_answer, keyboard=None):
    """Имитация нажатия клавиш ботом"""

    if message.forward_from is not None:  # Если сообщение является пересылаемым
        user_id = message.forward_from.id
    else:
        user_id = message.from_user.id

    # count_text_message = random.randint(1, 3)  # Случайное кол-во секунд будет имитироваться набор текста
    # count_text_message = float(int(0.1))
    count_text_message = len(text_answer) * 0.01
    # print(count_text_message)

    bot.send_chat_action(chat_id=user_id, action='typing')
    time.sleep(count_text_message)

    """Логирование действий в консоли"""

    if keyboard is None:
        bot.reply_to(message, text_answer)
    else:
        bot.send_message(chat_id=message.from_user.id,
                         text=text_answer,
                         reply_markup=keyboard)
    print(f'IT Remit info bot: "{text_answer}"\n')


log_file = Secret.way_to_log_telegram_bot


# def full_name_user(message):
#     """Принимает на вход сообщение. Возвращает имя пользователя: Администратор/Пользователь + Имя + ID"""
#
#     check_admin = SQL().check_for_admin(message.from_user.id)  # Проверяем является ли пользователь админом
#     if check_admin is True:
#         status_user = 'Администратор '
#     else:
#         status_user = 'Пользователь '
#     name_user = f'{message.from_user.first_name} (ID: {message.from_user.id})'  # Получаем имя и id
#     pattern = f'{time_now(message.date)}\n{status_user} {name_user}'  # Итог дата, /n, статус и данные пользователя
#     return pattern


def existence(message):
    # if message.forward_from is not None:  # Если сообщение является пересылаемым
    #     user_id = message.forward_from.id  # Получаем id человека полученного из пересылаемого сообщения
    # else:
    #     user_id = message.from_user.id
    user_id = message.chat.id

    # print(f'{full_name_user(message)} отправил команду:\n{message.text}')
    if SQL().check_for_existence(user_id) is True:  # Проверка на наличие юзера в БД
        SQL().collect_statistical_information(user_id)  # Счётчик активности пользователя
        SQL().update_data_user(user_id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username)
        return True
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


@bot.message_handler(commands=['start'])
@Decorators.registration_of_actions
def start_command(message):
    """Приветственное сообщение"""

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
        answer_bot(message, hello_message)
    else:  # Эта строка появится если уже зарегистрированный пользователь попытается заново пройти регистрацию
        end_text = f'Привет еще раз, {message.from_user.first_name}\nМы уже знакомы!\n' \
                   f'Список доступных команд тут -> /help'
        answer_bot(message, end_text)


@bot.message_handler(commands=['register'])
@Decorators.registration_of_actions
def register(message):
    """Регистрация данных о пользователе в БД"""

    if SQL().check_for_existence(message.from_user.id) is False:  # Если пользователь отсутствует в БД
        SQL().db_table_val(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username)
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
        answer_bot(message, register_message)
    else:  # Иначе бот уведомит о том что пользователь уже регистрировался
        end_text = f'Вы уже зарегистрированы!\nЧтобы узнать что умеет бот жми /help.'
        answer_bot(message, end_text)


@bot.message_handler(commands=['log_out'])
@Decorators.registration_of_actions
def log_out(message):
    """Удаление данных о пользователе из БД"""

    # print(f'{full_name_user(message)} отправил команду:\n{message.text}')
    if SQL().check_for_existence(message.from_user.id) is True:  # Если пользователь присутствует в БД
        SQL().log_out(message.from_user.id)  # Удаление данных из БД

        first_message = 'Подождите...'
        answer_bot(message, first_message)

        log_out_message = f'До новых встреч {message.from_user.first_name}!\n' \
                          f'Данные о вашем аккаунте успешно удалены!\n' \
                          f'Чтобы снова пользоваться функционалом бота, жми /register.'
        answer_bot(message, log_out_message)
    else:  # Иначе бот уведомит о том что пользователь ещё не регистрировался
        end_text = f'Нельзя удалить данные которых нет :)\nЧтобы это сделать, нужно зарегистрироваться!'
        answer_bot(message, end_text)


@bot.message_handler(commands=['help'])
@Decorators.registration_of_actions
def help_command(message):
    """Список доступных команд"""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        keyboard = telebot.types.InlineKeyboardMarkup()  # Вызов кнопки
        keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
        list_commands = can_help(message.from_user.id)
        answer_bot(message, list_commands, keyboard)
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_message = existence(message)
        answer_bot(message, end_message)


# bot.send_message(message.from_user.id, text='Главное меню', reply_markup=Menu_bot.Bot_menu().main_menu())


@bot.message_handler(commands=['invent'])
@Decorators.registration_of_actions
def invent(message):
    """Узнать кто следующий на инвентаризацию"""

    list_name = 'Инвентаризация'  # Имя страницы

    if rights_admin(message) is True:
        if Working_with_a_file(list_name).read_file() is not None:
            answer_message = Working_with_a_file(list_name).next_invent()
            sticker = Working_with_a_file(list_name).sticker_next_dej()

            answer_bot(message, answer_message)
            if sticker is not None:
                bot.send_sticker(message.chat.id, sticker)
        else:
            answer_message = Working_with_a_file(list_name).next_invent()
            answer_bot(message, answer_message)
    else:
        end_text = rights_admin(message)
        answer_bot(message, end_text)


@bot.message_handler(commands=['random'])
@Decorators.registration_of_actions
def random_name(message):
    """Получить имя дежурного на этой неделе из сисадминов"""

    if rights_admin(message) is True:
        list_name = ['Паша', 'Дима', 'Никита', 'Лёха']  # Список имён
        name_hero = random.choice(list_name)  # Получение случайного значения из списка
        # name_hero = File_processing.Working_with_a_file('Дежурный').read_file()[0][2]  # Имя ближайшего дежурного
        answer_bot(message, name_hero)
    else:
        end_text = rights_admin(message)
        answer_bot(message, end_text)


@bot.message_handler(commands=['set_admin'])
@Decorators.registration_of_actions
def set_to_admin(message):
    """Назначить пользователя админом"""

    if rights_admin(message) is True:
        answer_message = 'Чтобы назначить администратора, перешли мне сообщение от этого человека'
        answer_bot(message, answer_message)
        bot.register_next_step_handler(message, receive_id)  # Регистрация следующего действия
    else:
        end_text = rights_admin(message)
        answer_bot(message, end_text)


@Decorators.registration_of_actions
def receive_id(message):
    """Обработка пересланного сообщения"""
    try:
        id_future_admin = message.forward_from.id  # Получаем id человека полученного из пересылаемого сообщения
        first_name_future_admin = str(message.forward_from.first_name)  # Получаем имя будущего админа
        last_name_future_admin = str(message.forward_from.last_name)  # Получаем фамилию будущего админа
        full_name_future_admin = f'{first_name_future_admin} {last_name_future_admin}'  # Склеиваем данные воедино
        print(f'{message.from_user.first_name} (ID: {message.from_user.id}) переслал сообщение от пользователя '
              f'{full_name_future_admin} содержащее текст:\n {message.text}')
        answer_text = f'Пользователь <{full_name_future_admin}> добавлен в список администраторов'
        if SQL().check_for_existence(id_future_admin) is True:  # Проверка на наличие человека в БД
            if SQL().check_for_admin(id_future_admin) is False:  # Проверка админ ли юзер
                SQL().set_admin(id_future_admin)  # Обновляем статус нового админа в БД
                answer_bot(message, answer_text)
                message_from_new_admin = (f'Администратор <{message.from_user.first_name}> наделил вас правами '
                                          f'администратора')
                bot.send_message(id_future_admin, message_from_new_admin)  # Бот уведомляет пользователя, что такой-то
                # юзер, дал ему права админа
            else:  # Если тот кому предоставляют права уже админ, бот сообщит об ошибке
                end_text = 'Нельзя пользователю дать права администратора, поскольку он им уже является!'
                answer_bot(message, end_text)
        else:  # Если того кому пытаются дать права нет в БД, бот сообщит об ошибке
            end_text = 'Вы пытаетесь дать права администратора пользователю который отсутствует в базе данных!'
            answer_bot(message, end_text)
    except Exception:  # В любом другом случае бот сообщит об ошибке
        error_text = 'Что-то пошло не так. Чтобы попробовать снова, жми /set_admin'
        answer_bot(message, error_text)


@bot.message_handler(commands=['set_user'])
@Decorators.registration_of_actions
def set_to_user(message):
    """Лишить пользователя прав администратора"""

    if rights_admin(message) is True:
        answer_message = '• Чтобы пользователю присвоить статус <user>, перешлите мне сообщение от этого человека.\n' \
                         '• Если хотите отказаться от прав админа, в ответ пришлите сообщение с любым текстом.\n' \
                         '• Для отмены операции нажмите "Отмена".'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Отмена']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard)
        bot.register_next_step_handler(message, receive_id_user)  # Регистрация следующего действия
    else:
        end_text = rights_admin(message)
        answer_bot(message, end_text)


@Decorators.registration_of_actions
def receive_id_user(message):
    try:
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        if message.text == 'Отмена':
            answer_message = 'Операция прервана.'
            answer_bot(message, answer_message, hide_keyboard)
        else:
            chat_id = message.chat.id  # Получаем id чата
            id_future_user = chat_id  # Получаем id человека полученного из сообщения
            first_name_future_user = str(message.from_user.first_name)  # Получаем имя будущего юзера
            last_name_future_user = str(message.from_user.last_name)  # Получаем фамилию будущего юзера
            full_name_future_user = f'{first_name_future_user} {last_name_future_user}'  # Склеиваем данные воедино
            print(f'{message.from_user.first_name} (ID: {message.from_user.id}) переслал сообщение от пользователя '
                  f'{full_name_future_user} содержащее текст:\n {message.text}')
            answer_text = f'Пользователю <{full_name_future_user}> присвоен статус <user>'
            if SQL().check_for_existence(id_future_user) is True:  # Проверка на наличие человека в БД
                if SQL().check_for_admin(id_future_user) is True:  # Проверка админ ли юзер
                    SQL().set_user(id_future_user)  # Обновляем статус нового юзера в БД
                    answer_bot(message, answer_text, hide_keyboard)
                    bot.send_message(id_future_user, f'Администратор <{message.from_user.first_name}> лишил вас прав '
                                                     f'администратора')  # Бот уведомляет нового юзера, что
                    # пользователь <Имя>, лишил его прав админа
                else:  # Если тот, кого лишают прав админа, уже и так юзер, бот сообщит об ошибке
                    end_text = 'Нельзя пользователю присвоить статус <user> поскольку он им уже является'
                    answer_bot(message, end_text, hide_keyboard)
            else:  # Если того, кого пытаются лишить прав админа, нет в БД, бот сообщит об ошибке
                end_text = 'Вы пытаетесь присвоить пользователю статус <user>, который отсутствует в базе данных!'
                answer_bot(message, end_text, hide_keyboard)
    except Exception:  # В любом другом случае бот сообщит об ошибке
        error_text = 'Что-то пошло не так. Чтобы попробовать снова, жми /set_user'
        answer_bot(message, error_text)


@bot.message_handler(commands=['subscribe'])
@Decorators.registration_of_actions
def set_subscribe(message):
    """Подписка на рассылку"""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        if SQL().check_status_DB(message.from_user.id, 'notification',
                                 'yes') is False:  # Если пользователь не подписчик
            SQL().change_status_DB(message.from_user.id, 'notification')  # Присвоить статус <подписан>
            end_text = ('Подписка на уведомления активирована. Теперь вам будут приходить уведомления о том, '
                        'кто из системных администраторов дежурит в ближайшие выходные или праздничные дни, '
                        'кто в отпуске и прочая информация.\n\n'
                        '#####\n'
                        'В эту подписку не входят уведомления из барахолки! Внимательно ознакомьтесь со списком '
                        'доступных команд -> /help\n'
                        '#####\n\n'
                        'Чтобы отказаться от рассылки, жми /unsubscribe')
            answer_bot(message, end_text)
            #  Отсылка уведомлений о действии разработчику
            # bot.send_message(chat_id=dev_id,
            #                  text=f'{full_name_user(message)} подписался на уведомления.')
        else:  # Если подписчик пытается подписаться, то получит ошибку
            end_text = 'Вы уже подписаны на уведомления.'
            answer_bot(message, end_text)
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = existence(message)
        answer_bot(message, end_text)


@bot.message_handler(commands=['unsubscribe'])
@Decorators.registration_of_actions
def set_subscribe(message):
    if existence(message) is True:
        if SQL().check_status_DB(message.from_user.id, 'notification',
                                 'yes') is True:  # Если пользователь подписчик
            SQL().change_status_DB(message.from_user.id,
                                   'notification')  # Присвоить в БД статус <не подписан>
            end_text = 'Рассылка отключена.\n Чтобы подписаться жми /subscribe'
            answer_bot(message, end_text)
            #  Отсылка уведомлений о действии разработчику
            # bot.send_message(chat_id=dev_id,
            #                  text=f'{full_name_user(message)} отписался от уведомлений.')
        else:  # Если не подписчик пытается отписаться, то получит ошибку
            end_text = 'Нельзя отказаться от уведомлений на которые не подписан.'
            answer_bot(message, end_text)
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = existence(message)
        answer_bot(message, end_text)


@bot.message_handler(commands=['change_sticker'])
@Decorators.registration_of_actions
def change_sticker(message):
    """Присвоить/сменить себе стикер"""

    if rights_admin(message) is True:
        answer_message = 'Отправь мне стикер который хочешь привязать в своей учётной записи!'
        answer_bot(message, answer_message)
        bot.register_next_step_handler(message, change_sticker_step_2)  # Регистрация следующего действия
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = rights_admin(message)
        answer_bot(message, end_text)


# @Decorators.registration_of_actions
def change_sticker_step_2(message):
    # print(f'{full_name_user(message)} отправил стикер {message.sticker.file_id}')
    SQL().update_sqlite_table(message.sticker.file_id, message.from_user.id, 'sticker')
    end_text = 'Стикер обновлён'
    answer_bot(message, end_text)


@bot.message_handler(commands=['dezhurnyj'])
@Decorators.registration_of_actions
def dej(message):
    """Узнать кто дежурный"""

    if existence(message) is True:  # Проверка на наличие юзера в БД
        answer_message = 'Что вы хотите получить?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Имя следующего дежурного', 'Список дежурных']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard)
        bot.register_next_step_handler(message, dej_step_2)  # Регистрация следующего действия
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = existence(message)
        answer_bot(message, end_text)


@Decorators.registration_of_actions
def dej_step_2(message):
    sheet_name = 'Дежурный'
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Имя следующего дежурного':
        answer_message = Working_with_a_file(sheet_name).next_dej()
        user_sticker = Working_with_a_file(sheet_name).sticker_next_dej()
        # Пришлёт сообщение о дежурном
        answer_bot(message, answer_message, hide_keyboard)
        if user_sticker is not None:
            # Пришлёт стикер этого дежурного
            bot.send_sticker(message.chat.id, user_sticker)
    elif message.text == 'Список дежурных':
        count_data_list = len(Working_with_a_file(sheet_name).list_dej())
        answer_message = number_of_events(count_data_list)
        answer_bot(message, answer_message, keyboard=hide_keyboard)
        bot.register_next_step_handler(message, dej_step_3, sheet_name,
                                       count_data_list)  # Регистрация следующего действия


# @Decorators.registration_of_actions
def dej_step_3(message, sheet_name, count_data_list):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    count = int(message.text)
    if count <= count_data_list:
        data_list = Working_with_a_file(sheet_name).list_dej()
        Working_with_notifications.repeat_for_list(data_list, message.from_user.id, count)
    else:
        answer_message = f'Вы запрашиваете {count} записей, а есть только {count_data_list}.\n' \
                         f'Попробуйте снова - /dezhurnyj'
        answer_bot(message, answer_message, keyboard=hide_keyboard)


@bot.message_handler(commands=['get_list'])
@Decorators.registration_of_actions
def get_list(message):
    """Получить список всех пользователей"""

    if rights_admin(message) is True:
        answer_message = SQL().get_list_users()
        answer_bot(message, answer_message)
    else:  # Если пользователь не зарегистрирован, бот предложит это сделать
        end_text = rights_admin(message)
        answer_bot(message, end_text)


@bot.message_handler(commands=['feed_back'])
@Decorators.registration_of_actions
def feed_back(message):
    """Обратная связь"""

    answer_message = 'Выберите тип обращения'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Что-то не работает', 'Есть идея новой функции', 'Другое', 'Отмена']
    keyboard.add(*buttons)
    answer_bot(message, answer_message, keyboard=keyboard)
    bot.register_next_step_handler(message, feed_back_step_2)  # Регистрация следующего действия


@Decorators.registration_of_actions
def feed_back_step_2(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Обращение отменено.'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
    else:
        text_answer = 'Опишите суть обращения. Чем подробнее тем лучше.\n'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Отмена']
        keyboard.add(*buttons)
        answer_bot(message, text_answer, keyboard=keyboard)
        contacting_technical_support = f'{message.text}\n'
        bot.register_next_step_handler(message, feed_back_step_3,
                                       contacting_technical_support)  # Регистрация следующего действия


# @Decorators.registration_of_actions
def feed_back_step_3(message, text_problem):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Обращение отменено.'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
    else:
        answer_message = (f'Ваше обращение создано!\n'
                          f'Тип: {text_problem}\n'
                          f'Текст сообщения: {message.text}')
        answer_bot(message, answer_message, keyboard=hide_keyboard)
        bot.send_message(chat_id=dev_id,
                         text=f'Поступило новое обращение от пользователя:\n'
                              f'Тип: {text_problem}\n'
                              f'Текст сообщения: {message.text}')


@bot.message_handler(commands=['create_record'])
@Decorators.registration_of_actions
def create_record(message):
    """Создать уведомление"""

    if rights_admin(message) is True:
        answer_message = 'В какой лист добавить запись?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Уведомления для всех', 'Уведомления для подписчиков', 'Уведомления для админов', 'Отмена']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard=keyboard)
        bot.register_next_step_handler(message, create_record_step_2, buttons)  # Регистрация следующего действия
    else:
        end_text = rights_admin(message)
        answer_bot(message, end_text)


# @Decorators.registration_of_actions
def create_record_step_2(message, list_sheet):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Операция прервана.'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
    elif message.text not in list_sheet:
        answer_message = f'Нет листа с именем <{message.text}>! Необходимо выбрать из списка.'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Ок']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard=keyboard)
        bot.register_next_step_handler(message, create_record)  # Регистрация следующего действия
    else:
        list_of_answers = [message.text]
        answer_message = 'Введи текст уведомления'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
        bot.register_next_step_handler(message, create_record_step_3,
                                       list_of_answers)  # Регистрация следующего действия


# @Decorators.registration_of_actions
def create_record_step_3(message, list_of_answers):
    list_of_answers.append(message.text)
    answer_message = ('Введи дату когда уведомить о событии в формате <ДД.ММ.ГГГГ>.\n'
                      '*Примечание: если дату указать некорректно, уведомление не сработает!*')
    answer_bot(message, answer_message)
    bot.register_next_step_handler(message, create_record_step_4, list_of_answers)  # Регистрация следующего действия


# @Decorators.registration_of_actions
# noinspection PyTypeChecker
def create_record_step_4(message, list_of_answers):
    list_of_answers.append(message.text)

    sheet_name = list_of_answers[0]
    date = list_of_answers[2]
    text_event = list_of_answers[1]

    answer_message = Working_with_a_file(sheet_name).create_event(date, text_event)
    answer_bot(message, answer_message)
    list_of_answers.clear()

    exit()


@bot.message_handler(commands=['games'])
@Decorators.registration_of_actions
def games(message):
    """Игры"""

    answer_message = 'На данный момент доступна одна игра'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Играть в "Угадаю число"', 'Отмена']
    keyboard.add(*buttons)
    answer_bot(message, answer_message, keyboard=keyboard)
    bot.register_next_step_handler(message, games_step_2)  # Регистрация следующего действия


@Decorators.registration_of_actions
def games_step_2(message):
    if message.text == 'Играть в "Угадаю число"':
        answer_message = 'Хорошо, начнём. Правила просты - загадай число от 1 до 100 а я попробую его угадать. ' \
                         'Я называю число, если твоё число меньше, жми "меньше", если твоё число больше, ' \
                         'жми "больше", а если угадал - "в точку".'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Начнём']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard=keyboard)
        bot.register_next_step_handler(message, games_step_3)
    elif message.text == 'Отмена':
        answer_message = 'Хорошо, сыграем в другой раз.'
        answer_bot(message, answer_message)


@Decorators.registration_of_actions
def games_step_3(message):
    if message.text == 'Начнём':
        number = random.randint(0, 100)
        answer_message = f'Возможно это {number}?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Больше', 'Меньше', 'В точку']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard=keyboard)
        bot.register_next_step_handler(message, games_step_4, number, lower=1, high=100, count=1)


# @Decorators.registration_of_actions
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
        answer_bot(message, answer_message, keyboard=hide_keyboard)
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
    count += 1
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Больше', 'Меньше', 'В точку']
    keyboard.add(*buttons)
    answer_bot(message, answer_message, keyboard=keyboard)
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
@Decorators.registration_of_actions
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
        answer_bot(message, answer_message, keyboard=keyboard)
        bot.register_next_step_handler(message, check_defroster_step_2)  # Регистрация следующего действия
    else:
        answer_message = existence(message)
        answer_bot(message, answer_message)


@Decorators.registration_of_actions
def check_defroster_step_2(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Да':
        SQL().change_status_DB(message.from_user.id, 'def')  # Изменить текущий статус
        answer_message = 'Статус успешно изменён'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
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
            # bot.send_message(chat_id=dev_id,
            #                  text=f'{full_name_user(message)} начал отслеживать показания датчиков дефростеров.')

            answer_bot(message, end_message)
        else:
            if SQL().check_for_existence(message.from_user.id, 'tracking_sensor_defroster') is False:
                pass
            else:
                if SQL().get_mess_id(message.from_user.id) is not None:
                    message_id = SQL().get_mess_id(message.from_user.id)

                    Secret.bot.unpin_chat_message(chat_id=message.from_user.id, message_id=message_id)
                    Secret.bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

                SQL().log_out(message.from_user.id, 'tracking_sensor_defroster')

                end_message = 'Вы прекратили отслеживать показания. Если передумаете клик - /defrosters.'
                # bot.send_message(chat_id=dev_id,
                #                  text=f'{full_name_user(message)} прекратил отслеживать показания датчиков '
                #                       f'дефростеров.')

                answer_bot(message, end_message)
    elif message.text == 'Отмена':
        end_text = 'Операция прервана'
        answer_bot(message, end_text)


@bot.message_handler(commands=['all_sensors'])
@Decorators.registration_of_actions
def check_error_sensor(message):
    if SQL().check_status_DB(message.from_user.id, 'observer_all_sensor', 'yes') is False:
        answer_message = ('Инструмент позволяет отслеживать неисправные термодатчики. Вам придёт авто-обновляемое '
                          'сообщение со списком. А так же будут поступать сообщения как только обнаружится '
                          'неисправность. На данный момент вы не подписаны на уведомления. Хотите начать?\n'
                          '*** выберите действие ниже ***')
    else:
        answer_message = ('На данный момент вы подписаны на уведомления о неисправных датчиках. '
                          'Прекратить отслеживать?\n'
                          '*** выберите действие ниже ***')
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Да', 'Отмена']
    keyboard.add(*buttons)
    answer_bot(message, answer_message, keyboard=keyboard)
    bot.register_next_step_handler(message, check_error_sensor_step_2)  # Регистрация следующего действия


@Decorators.registration_of_actions
def check_error_sensor_step_2(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Да':
        SQL().change_status_DB(message.from_user.id, 'observer_all_sensor')  # Изменить текущий статус
        answer_message = 'Статус успешно изменён'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
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
            # bot.send_message(chat_id=dev_id,
            #                  text=f'{full_name_user(message)} начал отслеживать список неисправных датчиков.')

            answer_bot(message, end_message)
        else:  # Если пользователь не подписан на отслеживание показаний
            # Проверка на наличие пользователя в БД
            if SQL().check_for_existence(message.from_user.id, 'observers_for_faulty_sensors') is False:
                pass
            else:
                if SQL().get_mess_id(message.from_user.id) is not None:
                    message_id = SQL().get_mess_id(message.from_user.id)

                    Secret.bot.unpin_chat_message(chat_id=message.from_user.id, message_id=message_id)
                    Secret.bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

                SQL().log_out(message.from_user.id, 'observers_for_faulty_sensors')

                end_message = 'Вы прекратили отслеживать список неисправных датчиков. ' \
                              'Если передумаете клик - /all_sensors.'
                # bot.send_message(chat_id=dev_id,
                #                  text=f'{full_name_user(message)} прекратил отслеживать список неисправных датчиков.')

                answer_bot(message, end_message)
    elif message.text == 'Отмена':
        end_text = 'Операция отменена'
        answer_bot(message, end_text)


@bot.message_handler(commands=['answer'])
@Decorators.registration_of_actions
def answer(message):
    if message.from_user.id == dev_id:
        if SQL().count_not_answer() > 0:
            answer_message = SQL().search_not_answer()
            message_bot = f'Как ответить на это сообщение?\n<{answer_message}>'
            answer_bot(message, message_bot)
            bot.register_next_step_handler(message, answer_step_two, answer_message)
        else:
            message_bot = SQL().search_not_answer()
            answer_bot(message, message_bot)


# @Decorators.registration_of_actions
def answer_step_two(message, question):
    text_answer = message.text
    SQL().update_answer_speak_DB(question, text_answer)

    message_bot = 'Запомнил. Продолжим? /answer'
    answer_bot(message, message_bot)


@bot.message_handler(commands=['vacation'])
@Decorators.registration_of_actions
def get_number_vacation_days(message):
    """Функция возвращает кол-во накопившихся дней отпуска либо текст с описанием при возникновении ошибки."""

    if existence(message) is True:
        if SQL().check_verify_in_ERP(message.from_user.id) is True:
            count_day = ERP.Exchange_with_ERP({Secret.number: message.from_user.id}).answer_from_ERP()
            if isinstance(count_day, int):
                days = declension_day(count_day)
                answer_message = f'На данный момент у вас накоплено ||{count_day} {days}|| отпуска'
                # types_message(message)
                bot.send_message(chat_id=message.from_user.id, text=answer_message, parse_mode='MarkdownV2')
                print(f'{answer_bot}На данный момент у вас накоплено &&& дней отпуска\n')
                logging_telegram_bot('info',
                                     f'Пользователь {message.from_user.first_name}({message.from_user.id}) '
                                     f'получил ответ от ERP по кол-ву накопленных дней отпуска.')
            else:
                answer_message = str(count_day)  # Тут текст ошибки
                answer_bot(message, answer_message)
        else:
            verify_error = 'Чтобы воспользоваться функцией необходимо пройти верификацию в 1С -> /verification'
            answer_bot(message, verify_error)
    else:
        answer_message = existence(message)
        bot.reply_to(message, answer_message)


@bot.message_handler(commands=['verification'])
@Decorators.registration_of_actions
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
        answer_bot(message, answer_message, keyboard=keyboard)
        bot.register_next_step_handler(message, verification_step_2)  # Регистрация следующего действия
    else:
        answer_message = existence(message)
        answer_bot(message, answer_message)


@Decorators.registration_of_actions
def verification_step_2(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Ок':
        answer_message = 'Введите номер вашего ИНН'
        answer_bot(message, answer_message, keyboard=hide_keyboard)
        bot.register_next_step_handler(message, verification_step_3)  # Регистрация следующего действия
    elif message.text == 'Отмена':
        end_text = 'Операция прервана. Когда будете готовы клик -> /verification'
        answer_bot(message, end_text)


@Decorators.registration_of_actions
def verification_step_3(message):
    if len(message.text) == 12:
        answer_message = ERP.Exchange_with_ERP(
            {Secret.number: message.from_user.id, Secret.verification: message.text}).answer_from_ERP()
        answer_bot(message, answer_message)
        SQL().update_sqlite_table('yes', message.from_user.id, 'verify_erp')
    else:
        error_text = 'Не удалось выполнить запрос. Номер ИНН должен состоять из 12 символов и содержать ' \
                     'только цифры. Проверьте корректно ли вы указали данные. Попробуйте снова -> /verification'
        answer_bot(message, error_text)


@bot.message_handler(commands=['baraholka'])
@Decorators.registration_of_actions
def baraholka(message):
    user_id = message.from_user.id
    if existence(message) is True:
        status = ''
        if SQL().check_status_bar(user_id) is True:
            status = 'вы подписаны на уведомления!'
        elif SQL().check_status_bar(user_id) is False:
            status = 'вы не подписаны на уведомления\n' \
                     'Как только вы активируете подписку, вам будут присланы все те лоты которые ещё не забрали.\n' \
                     'Не пугайтесь, их может быть много! А может и ни одного :)\n' \
                     'Чтобы понять как работает барахолка, настоятельно рекомендуем ознакомиться с описанием!'

        text_to_user = f'Давно не виделись {message.from_user.first_name}! В данный момент {status}'
        answer_bot(message, text_to_user)
        time.sleep(3)

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Изменить статус', 'Оставить как есть']
        manual = ['Как это работает?']
        keyboard.add(*buttons)
        keyboard.add(*manual)
        # types_message(message)
        text_to_user = 'Выберите действие:'
        answer_bot(message, text_to_user, keyboard)
        bot.register_next_step_handler(message, baraholka_step_2)
    else:
        answer_message = existence(message)
        answer_bot(message, answer_message)


@Decorators.registration_of_actions
def baraholka_step_2(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Изменить статус':
        answer_SQL = SQL().change_status_bar(message.from_user.id)
        text_to_user = f'Статус успешно изменён!\n{answer_SQL}'
        answer_bot(message, text_to_user, hide_keyboard)
    elif message.text == 'Оставить как есть':
        text_to_user = 'Хорошо. До новых сообщений! ;)'
        answer_bot(message, text_to_user, hide_keyboard)
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

        answer_bot(message, manual, hide_keyboard)


@bot.message_handler(commands=['place_a_lot'])
@Decorators.registration_of_actions
def place_a_lot(message):
    # user_id = message.from_user.id
    if rights_admin(message) is True:
        text_answer = 'Для создания лота, необходимо\n' \
                      '• Дать ему название\n' \
                      '• Прикрепить фото\n' \
                      '• Краткое описание\n\n' \
                      '*Выбери действие*'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Создать лот', 'Возможно позже']
        keyboard.add(*buttons)
        answer_bot(message, text_answer, keyboard)
        bot.register_next_step_handler(message, place_a_lot_step_2)
    else:
        answer_message = existence(message)
        answer_bot(message, answer_message)


@Decorators.registration_of_actions
def place_a_lot_step_2(message):
    # user_id = message.from_user.id
    name_lot = None
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Создать лот':
        answer_text = 'Как будет называться лот?'
        answer_bot(message, answer_text, hide_keyboard)
        bot.register_next_step_handler(message, place_a_lot_step_3, name_lot)
    elif message.text == 'Возможно позже':
        answer_text = 'Создание лота отменено.'
        answer_bot(message, answer_text, hide_keyboard)


# @Decorators.registration_of_actions
def place_a_lot_step_3(message, name_lot):
    # user_id = message.from_user.id
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if name_lot is None:
        name_lot = message.text
    else:
        name_lot = name_lot

    answer_text = 'Теперь отправь мне фотографию лота.\n' \
                  '*Примечание: при отправке нескольких фото, будет использоваться первая прикреплённая!'

    answer_bot(message, answer_text, hide_keyboard)
    bot.register_next_step_handler(message, place_a_lot_step_4, name_lot)


# @Decorators.registration_of_actions
def place_a_lot_step_4(message, name_lot):
    if message.photo is not None:
        photo_id = message.photo[0].file_id
        answer_text = 'Теперь нужно добавить описание к лоту (что это, рабочее ли состояние, возможные дефекты)'
        answer_bot(message, answer_text)
        bot.register_next_step_handler(message, place_a_lot_step_5, name_lot, photo_id)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Ещё попытка']
        keyboard.add(*buttons)
        answer_text = 'Не спеши! На данном этапе мне нужна фотография. Попробуем ещё раз. Нажми на кнопку ниже'
        answer_bot(message, answer_text, keyboard)
        bot.register_next_step_handler(message, place_a_lot_step_3, name_lot)


# @Decorators.registration_of_actions
def place_a_lot_step_5(message, name_lot, photo_id):
    description_lot = message.text

    answer_text = 'Указать стоимость лота?\n' \
                  '*Выберите действие*'

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Указать цену', 'Бесплатно']
    keyboard.add(*buttons)
    answer_bot(message, answer_text, keyboard)
    bot.register_next_step_handler(message, place_a_lot_step_6, name_lot, photo_id, description_lot)


# @Decorators.registration_of_actions
def place_a_lot_step_6(message, name_lot, photo_id, description_lot):
    # user_id = message.from_user.id

    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Указать цену':
        answer_text = 'Сколько будет стоить лот?'
        answer_bot(message, answer_text, hide_keyboard)
        bot.register_next_step_handler(message, place_a_lot_step_7, name_lot, photo_id, description_lot)
    elif message.text == 'Бесплатно':
        price = "бесплатно"
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Продолжить']
        keyboard.add(*buttons)
        answer_text = 'Для того чтобы продолжить нажмите кнопку ниже'
        answer_bot(message, answer_text, keyboard)
        bot.register_next_step_handler(message, place_a_lot_step_8, name_lot, photo_id, description_lot, price)


# @Decorators.registration_of_actions
def place_a_lot_step_7(message, name_lot, photo_id, description_lot):
    price = f'{message.text}₽'
    if message.text is not None:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Продолжить']
        keyboard.add(*buttons)
        answer_text = 'Для того чтобы продолжить нажмите кнопку ниже'
        answer_bot(message, answer_text, keyboard)
        bot.register_next_step_handler(message, place_a_lot_step_8, name_lot, photo_id, description_lot, price)
    else:
        answer_text = "Кажется вы забыли указать цену! Укажите её прямо сейчас:"
        answer_bot(message, answer_text)
        bot.register_next_step_handler(message, place_a_lot_step_7, name_lot, photo_id, description_lot)


# @Decorators.registration_of_actions
def place_a_lot_step_8(message, name_lot, photo_id, description_lot, price):
    lot_number = Working_with_notifications.Notification().get_last_record_lots() + 1
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Разместить', 'Создать заново', 'Удалить пост']
    keyboard.add(*buttons)
    answer_text = 'Вот так пользователи будут видеть созданный лот:\n' \
                  '*Выбери действие*'

    answer_bot(message, answer_text, keyboard)
    bot.send_photo(message.chat.id,
                   caption=f'Лот №{lot_number}\n\n'
                           f'Название: {name_lot}\n\n'
                           f'Описание: {description_lot}\n\n'
                           f'Стоимость: {price}\n\n',
                   photo=photo_id)
    bot.register_next_step_handler(message, place_a_lot_step_9, name_lot, photo_id, description_lot, price)


# @Decorators.registration_of_actions
def place_a_lot_step_9(message, name_lot, photo_id, description_lot, price):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Разместить':
        SQL().record_lot_to_DB(name_lot, photo_id, description_lot)  # Помещаем имя, id фото и описание в БД
        Notification().notification_for_subs_lots(name_lot, photo_id, description_lot, price)  # Рассылка подписчикам
        id_callback_data = Notification().get_last_record_lots()  # Получаем id последнего лота из БД
        keyboard = telebot.types.InlineKeyboardMarkup()  # Инициализация клавиатуры
        button = telebot.types.InlineKeyboardButton(text='Забронировать лот', callback_data=id_callback_data)
        keyboard.add(button)

        answer_text = 'Лот успешно разослан подписчикам барахолки!'
        answer_bot(message, answer_text, hide_keyboard)
    elif message.text == 'Создать заново':
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Начать']
        keyboard.add(*buttons)
        answer_text = 'Для того чтобы продолжить нажмите кнопку ниже'
        answer_bot(message, answer_text, keyboard)
        bot.register_next_step_handler(message, place_a_lot)
    elif message.text == 'Удалить пост':
        answer_text = 'Публикация поста отменена'
        answer_bot(message, answer_text, hide_keyboard)


@bot.message_handler(commands=['urgent_message'])
@Decorators.registration_of_actions
def urgent_message(message):
    if rights_admin(message) is True:
        answer_message = 'Кому вы собираетесь разослать сообщение?'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Всем пользователям', 'Подписчикам', 'Админам', 'Барахольщикам', 'Отмена']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard)
        bot.register_next_step_handler(message, urgent_message_step_2, buttons)  # Регистрация следующего действия
    else:
        end_text = rights_admin(message)
        answer_bot(message, end_text)


# @Decorators.registration_of_actions
def urgent_message_step_2(message, list_sheet):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Отмена':
        answer_message = 'Операция прервана.'
        answer_bot(message, answer_message, hide_keyboard)
    elif message.text not in list_sheet:
        answer_message = f'"{message.text}" не подходит.. Необходимо выбрать из списка!'
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Ок']
        keyboard.add(*buttons)
        answer_bot(message, answer_message, keyboard)
        bot.register_next_step_handler(message, create_record)  # Регистрация следующего действия
    else:
        list_of_answers = [message.text]
        answer_message = 'Введи текст уведомления'
        answer_bot(message, answer_message, hide_keyboard)
        bot.register_next_step_handler(message, urgent_message_step_3,
                                       list_of_answers)  # Регистрация следующего действия


# @Decorators.registration_of_actions
def urgent_message_step_3(message, list_of_answers):
    list_of_answers.append(message.text)

    sheet_name = list_of_answers[0]
    text_event = list_of_answers[1]

    end_message = ''

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
        answer_bot(message, error_message, keyboard)

    confirm_message = f'Уведомление будет выглядеть вот так: \n•••••\n' \
                      f'{end_message}\n•••••\n' \
                      f'Отправить его?\n' \
                      f'*Выберите действие*'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Да', 'Отмена']
    keyboard.add(*buttons)
    answer_bot(message, confirm_message, keyboard)
    bot.register_next_step_handler(message, urgent_message_step_4, list_of_answers)  # Регистрация следующего действия


# @Decorators.registration_of_actions
def urgent_message_step_4(message, list_of_answers):
    sheet_name = list_of_answers[0]
    text_event = list_of_answers[1]

    if message.text == 'Да':
        if sheet_name == 'Всем пользователям':
            end_message = f'• Уведомление для зарегистрированных пользователей •\n\n' \
                          f'{text_event}'
            Working_with_notifications.Notification().send_a_notification_to_all_users(end_message)
        elif sheet_name == 'Подписчикам':
            end_message = f'• Уведомление для подписчиков •\n\n' \
                          f'{text_event}'
            Working_with_notifications.Notification().send_notification_to_subscribers(end_message)
        elif sheet_name == 'Админам':
            end_message = f'• Уведомление для администраторов •\n\n' \
                          f'{text_event}'
            Working_with_notifications.Notification().send_notification_to_administrators(
                end_message)
        elif sheet_name == 'Барахольщикам':
            end_message = f'• Уведомление для подписчиков барахолки •\n\n' \
                          f'{text_event}'
            Working_with_notifications.Notification().notification_for_sub_baraholka(end_message)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()  # Вызов кнопки
            keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
            error_message = 'Что-то пошло не так. Обратитесь к разработчику.'
            answer_bot(message, error_message, keyboard)
    elif message.text == 'Отмена':
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        answer_message = 'Операция прервана.'
        answer_bot(message, answer_message, hide_keyboard)

    exit()


@bot.message_handler(commands=['secret_santa'])
@Decorators.registration_of_actions
def secret_santa(message):
    current_year = datetime.datetime.now().year
    date_start = datetime.datetime.strptime(f'{current_year}-11-01', '%Y-%m-%d').date()
    date_finish = datetime.datetime.strptime(f'{current_year}-11-30', '%Y-%m-%d').date()

    if date_start <= datetime.date.today() <= date_finish:  # Если дата в диапазоне
        # print(f'{datetime.date.today()} в диапазоне между {date_start} и {date_finish}')
        if SQL().check_verify_in_ERP(message.from_user.id) is True:
            user_name = message.from_user.first_name
            hello_message = (f'Привет {user_name}!\n'
                             f'Уже совсем скоро наступят новогодние праздники. А какой самый главный атрибут '
                             f'любого праздника? Конечно подарки! Возможно ты уже участвовал(а) в подобном мероприятии,'
                             f' а если нет - жми кнопку узнать правила.')

            link_picture = 'https://6404332.ru/wa-data/public/shop/products/76/75/7576/images/10067/10067.750x0.jpg'
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ['Узнать правила', 'Отмена']
            keyboard.add(*buttons)

            bot.send_photo(chat_id=message.from_user.id,
                           photo=link_picture,
                           caption=hello_message,
                           reply_markup=keyboard)
            bot.register_next_step_handler(message, secret_santa_step_2)  # Регистрация следующего действия
        else:
            verify_error = 'Чтобы принять участие необходимо пройти верификацию в 1С -> /verification'
            answer_bot(message, verify_error)
    else:
        format_date_start = date_start.strftime('%d.%m.%Y')
        format_date_finish = date_finish.strftime('%d.%m.%Y')
        error_text = (f'Начать регистрацию на участие в проведении "Тайного Санты" можно в '  # noqa
                      f'период с {format_date_start} по {format_date_finish}')
        answer_bot(message, error_text)


@Decorators.registration_of_actions
def secret_santa_step_2(message):
    rules = (f'Бюджет для подарка вы определяете сами, но ширина кармана у всех разная, поэтому не стоит ожидать, что '
             f'Porsche или Cartier лучшая мысль :)\nЕсли вам сложно определиться с суммой, давайте условимся о '
             f'диапазоне 1000-2000р.\n\n'
             f'Теперь о правилах проведения:\n'
             f'• Каждый участник делится своими пожеланиями о том, что бы они хотели получить (например '
             f'энциклопедию о народе Майя, весёлую кружку или тотем медведя), и тем, что точно не хочется '
             f'получить (например вы не любите шоколад, категоричны к спиртному или боитесь снеговиков).\n'
             f'• Вам будет присвоено случайное уникальное имя, но узнаете вы его в день вручения подарков. Для '
             f'чего оно нужно, спросите вы? Для того, кто будет готовить подарок для вас!\n'
             f'• Когда регистрация всех участников завершится, каждому будет подобран случайный участник из '
             f'списка, но вы не узнаете кто он(а). Всё что вам будет доступно, это вымышленное имя и то какие '
             f'предпочтения по подарку он(а) указал(а). Пока в офисе не нарядили ёлку, у вас будет время на '
             f'подбор подходящего подарка.\n'
             f'• После чего приходите к секретарю, берёте подарочный пакет и распечатанный псевдоним того, '
             f'кто вам выпал, упаковываете его, крепите лист с именем и ставите под ёлку.\n'
             f'• В день распределения подарков вам придёт уведомление с именем которое выпало вам.\n\n'
             f'На этом всё, ищите ваш псевдоним под ёлкой :)\n'
             f'***\nЧтобы всё прошло гладко, будьте честными с собой и соблюдайте правила. Прежде чем пройти '
             f'регистрацию решите для себя, уверены ли вы в своих намерениях довести дело до конца.\n'
             f'Так же есть вероятность, что вам не достанется "пары" поскольку для участия нужно чётное количество '
             f'людей\n***')
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Пройти регистрацию', 'Не хочу участвовать']
    hide_keyboard = telebot.types.ReplyKeyboardRemove()

    keyboard.add(*buttons)

    if message.text == 'Узнать правила':
        answer_bot(message, rules, keyboard)
        bot.register_next_step_handler(message, secret_santa_step_3)  # Регистрация следующего действия
    elif message.text == 'Отмена':
        answer_bot(message, 'Я вас понял. Если передумаете клик -> /secret_santa', hide_keyboard)


@Decorators.registration_of_actions
def secret_santa_step_3(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Пройти регистрацию':
        user_id = message.from_user.id
        if SQL().check_user_in_table_secret_santa(user_id=user_id) is False:
            user_name = message.from_user.first_name

            SQL().registration_secret_santa(user_id, user_name)
            answer_bot(message, 'Вы успешно зарегистрированы! Теперь перечислите те вещи, которые вам не '
                                'хотелось бы получить в подарок', hide_keyboard)
            bot.register_next_step_handler(message, secret_santa_step_4)  # Регистрация следующего действия
        else:
            answer_bot(message, 'Вы уже являетесь участником жеребьёвки', hide_keyboard)
    elif message.text == 'Не хочу участвовать':
        answer_bot(message, 'Не знаете от чего отказываетесь ;)\nЕсли передумаете клик -> /secret_santa',
                   hide_keyboard)


@Decorators.registration_of_actions
def secret_santa_step_4(message):
    answer_message = 'Супер! Теперь расскажите о том, что для вас было бы желанным подарком'
    answer_bot(message, answer_message)
    bad_gift = message.text
    bot.register_next_step_handler(message, secret_santa_step_5, bad_gift)  # Регистрация следующего действия


# @Decorators.registration_of_actions
def secret_santa_step_5(message, bad_gift):
    good_gift = message.text
    user_id = message.from_user.id
    SQL().update_data_secret_santa(user_id=user_id, good_gift=good_gift, bad_gift=bad_gift)
    answer_text = ('Всё прошло успешно! Данные записаны. Ожидайте регистрации всех участников. В следующем этапе вы '
                   'получите вводные о том кому и что готовить. Немного терпения, скоро начнём! :)')
    answer_bot(message, answer_text)


@bot.message_handler(commands=['creative_nickname'])
@Decorators.registration_of_actions
def creative_santa_name(message):
    current_year = datetime.datetime.now().year
    date_start = datetime.datetime.strptime(f'{current_year}-02-01', '%Y-%m-%d').date()
    date_finish = datetime.datetime.strptime(f'{current_year}-10-29', '%Y-%m-%d').date()

    if date_start <= datetime.date.today() <= date_finish:  # Если дата в диапазоне
        name_user = message.from_user.first_name
        availability = src.Other_functions.Functions.SQL().checking_for_availability_in_cnn(message.from_user.id)
        count_symbol = 20
        hello_message = ''
        rules = ('  Оно должно быть новогоднее или как-то связано с Ремитом, возможно состоящее из '
                 f'нескольких слов, главное не длиннее {count_symbol} '
                 f'{declension(count_symbol, "символ", "символа", "символов")}. '
                 f'Например "Оливье", "Дед мороз" или "Почти директор"\n\n'
                 f'••• Выбери действие ниже •••')

        if availability is False:
            hello_message = (f'Привет {name_user}!\n    Очень нужна твоя креативная помощь! Мы тут кое к чему '
                             f'готовимся, и без тебя никак! Нужно придумать короткое и лаконичное имя для участие в '
                             f'игре о которой все узнают немного позже.\n')
        else:
            hello_message = (f'Давно не виделись {name_user}!\n Рассказывай, что удалось придумать :)\nНапомню правила '
                             f'составления имён:\n')

        answer_message = f'{hello_message}{rules}'

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Предложить псевдоним', 'Возможно позже']
        keyboard.add(*buttons)

        answer_bot(message, answer_message, keyboard)
        bot.register_next_step_handler(message, creative_santa_name_step_2)
    else:
        next_date = datetime.datetime.strptime(f'{current_year + 1}-02-01', '%Y-%m-%d').date()
        format_date = next_date.strftime('%d.%m.%Y')
        answer_message = f'Функция станет доступна после {format_date}'
        answer_bot(message, answer_message)


@Decorators.registration_of_actions
def creative_santa_name_step_2(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()

    if message.text == 'Предложить псевдоним':
        answer_message = 'Хорошо, как будет звучать имя?'
        answer_bot(message, answer_message, hide_keyboard)
        bot.register_next_step_handler(message, creative_santa_name_step_3)  # Регистрация следующего действия
    elif message.text == 'Возможно позже':
        answer_bot(message, 'Я вас понял. Если передумаете клик -> /creative_nickname', hide_keyboard)


@Decorators.registration_of_actions
def creative_santa_name_step_3(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()

    nickname = message.text
    length_nickname = len(nickname)
    count_symbol = 20
    declension_symbol = declension(length_nickname, "символ", "символа", "символов")

    if length_nickname <= count_symbol:
        format_nickname = f'#{nickname.lower().replace(" ", "_")}'
        having_a_name_DB = src.Other_functions.Functions.SQL().check_nickname_in_db(format_nickname)
        if having_a_name_DB is False:
            src.Other_functions.Functions.SQL().record_nickname_from_db(message.from_user.id, format_nickname)
            text_mes_from_dev = 'Пользователь предложил новое имя для Тайного Санты -> /approve_nickname'
            bot.send_message(chat_id=dev_id, text=text_mes_from_dev)
            answer_message = (f'"{nickname}" звучит отлично! Имя отправлено на модерацию. Если оно будет одобрено, вам '
                              f'придёт уведомление. Спасибо что помогаете развитию проектов!\n'
                              f'Есть ещё идеи? Жми -> /creative_nickname')
            answer_bot(message, answer_message, hide_keyboard)
        else:
            answer_message = f'Такое имя уже кто-то придумал. Попробуйте ещё :) -> /creative_nickname'
            answer_bot(message, answer_message, hide_keyboard)
    else:
        # print(f'"{text}" = {len(text)}\nТекст не должен превышать {count_symbol} символов')
        answer_message = (f'Не подходит :(\n'
                          f'Длина "{nickname}" составляет {length_nickname} {declension_symbol}.\n'
                          f'Суммарно имя не должно превышать {count_symbol} '
                          f'{declension(count_symbol, "символ", "символа", "символов")}\n'
                          f'Сократите количество на {length_nickname - count_symbol} и попробуйте снова.'
                          f'Чтобы попробовать снова -> /creative_nickname')
        answer_bot(message, answer_message, hide_keyboard)


@bot.message_handler(commands=['approve_nickname'])
@Decorators.registration_of_actions
def approve_nickname(message):
    if message.from_user.id == dev_id:
        nickname = src.Other_functions.Functions.SQL().check_not_approve_nickname()
        if nickname is not None:
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ['Одобрить', 'Отклонить']
            keyboard.add(*buttons)

            answer_message = f'Что делаем с ником "{nickname}"?'

            answer_bot(message, answer_message, keyboard)
            bot.register_next_step_handler(message, approve_nickname_step_2, nickname)
        else:
            answer_message = 'Все псевдонимы обработаны'
            answer_bot(message, answer_message)


def approve_nickname_step_2(message, nickname):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    answer_message = ''
    if message.text == 'Одобрить':
        status_approve = 1
        id_user_in_db = src.Other_functions.Functions.SQL().approve_nickname(nickname, status_approve)
        answer_message = f'Никнейм "{nickname}" одобрен.'
    elif message.text == 'Отклонить':
        status_approve = 0
        id_user_in_db = src.Other_functions.Functions.SQL().approve_nickname(nickname, status_approve)
        answer_message = f'Никнейм "{nickname}" отклонён.'

    end_text = f'{answer_message}\nПродолжим? -> /approve_nickname'
    answer_bot(message, end_text, hide_keyboard)

    message_to_user = f'Недавно вы предлагали псевдоним. Как и обещал, вернулся с ответом:\n{answer_message}'
    bot.send_message(chat_id=id_user_in_db, text=message_to_user)


@bot.callback_query_handler(func=lambda c: True)
# @Decorators.registration_of_actions
def inline(c):
    user_id = c.from_user.id  # Получаем user_id
    user_name = c.from_user.first_name  # Получаем имя пользователя
    dict_data = string_to_dict(c.data)  # Получаем dict(словарь) из входных данных
    key = [key for key in dict_data.keys()][0]  # Достаём ключ из словаря
    number_lot = dict_data.get(key)  # Достаём значение из словаря

    SQL().collect_statistical_information(user_id)
    print(user_id)
    print(key)
    print(number_lot)
    print(c.data)
    print(c)
    if key == 'lot':
        print('key == lot')
        answer_sql = SQL().booked_lots(number_lot, user_id)  # Попытка юзером забронировать лот
        print(f'answer_sql = {answer_sql}')
        if answer_sql != 'Success':  # Если лот забронирован
            print('Нельзя забронировать лот')
            bot.answer_callback_query(c.id, text=answer_sql)  # Вызывает у юзера всплывающее окно с текстом ошибки
        elif answer_sql == 'Success':  # Если лот не забронирован
            count_booked_lot = SQL().count_booked_lot(user_id)
            answer_text = f'Использовано {count_booked_lot} из 3 броней'
            bot.answer_callback_query(c.id, text=answer_text)
            SQL().edit_message_lots(number_lot)  # Пользователь бронирует лот за собой и у всех подписчиков в этом
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

    # SQL().schedule_updating_data_on_lots()


@bot.message_handler(content_types=['text'])
@Decorators.registration_of_actions
def speak(message):
    text_message_user = message.text.capitalize()  # Делаем все буквы строчными
    the_answer_to_the_question = SQL().talk(text_message_user)  # Поиск ответа в БД
    if the_answer_to_the_question is None:  # Если ответа в БД нет
        end_text = f'{random.choice(Secret.list_answer_speak)}\nГоворите со мной чаще, я научусь!'
        answer_bot(message, end_text)

        count = SQL().count_not_answer()
        how_much = declension(count, 'вопрос', 'вопроса', 'вопросов')
        end_message = f'На данный момент есть {count} {how_much} без ответа. Ответить на вопросы - /answer'
        bot.send_message(chat_id=dev_id, text=end_message)
    else:
        answer_bot(message, the_answer_to_the_question)


@bot.message_handler(content_types=['photo'])
@Decorators.registration_of_actions
def return_data_of_message(message):
    print(message)


if __name__ == '__main__':
    while True:
        try:
            text_message = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n' \
                           f'Telegram_bot.py начал работу\n'
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
        except Secret.telebot.apihelper.ApiTelegramException as error_telegram:
            time.sleep(3)
            text_error = f'ApiTelegramException:\n{error_telegram}'
            bot.send_message(chat_id=dev_id, text=text_error)
            print(str(text_error))
        except Exception as e:
            time.sleep(3)

            #  Получить имя модуля в котором сработало исключение
            frm = inspect.trace()[-1]
            file_name = frm[1]
            line_error = frm[2]

            text = (f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                    f'Сработало исключение: "{e}"\n'
                    f'Имя файла: {file_name}\n'
                    f'Строка: {line_error}\n')

            bot.send_message(chat_id=dev_id, text=text)
            print(text)
            logging_telegram_bot('error', text_log=text)
        # except BaseException:  # noqa
        #     print(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
        #           f'Возникла ошибка типа передаваемых данных')
