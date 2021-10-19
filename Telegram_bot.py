import datetime
import os
import random
import time

import telebot

import Clear_old_data
import Data
import Read_file
import SQLite
import What_i_can_do

bot = Data.bot

now_date = datetime.datetime.now()
now_date = now_date.strftime("%d.%m.%Y %H:%M:%S")

answer_bot = 'Бот ответил:\n'


def full_name_user(message):
    check_admin = SQLite.check_for_admin(message.from_user.id)
    if check_admin == 'True':
        status_user = 'Администратор '
    else:
        status_user = 'Пользователь '
    name_user = message.from_user.first_name + ' (ID: ' + str(message.from_user.id) + ') '
    pattern = now_date + '\n' + status_user + name_user
    return pattern


@bot.message_handler(commands=['start'])
def start_command(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'False':  # Если пользователь отсутствует в БД
        # Приветственное сообщение
        hello_message = 'Добро пожаловать ' + message.from_user.first_name + '\n' + \
                        'Для того чтобы пользоваться функциями бота, необходимо пройти регистрацию нажав /register. ' \
                        'Тем самым вы даёте согласие на хранение и обработку данных о вашем аккаунте. В базу данных ' \
                        'будут занесены следующие сведения:\n ' + \
                        'ID: ' + str(message.from_user.id) + '\n' + \
                        'Имя: ' + str(message.from_user.first_name) + '\n' + \
                        'Фамилия: ' + str(message.from_user.last_name) + '\n' + \
                        'Username:  @' + str(message.from_user.username) + '\n'
        Data.bot.send_message(message.from_user.id, hello_message)
        print(answer_bot)
    else:
        end_text = 'Привет еще раз, ' + message.from_user.first_name + '\n' + 'Мы уже знакомы!'
        Data.bot.send_message(message.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


#  Регистрация данных о пользователе в БД
@bot.message_handler(commands=['register'])
def register(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'False':  # Если пользователь отсутствует в БД
        register_message = 'Добро пожаловать ' + message.from_user.first_name + '\n' + \
                           'Вы успешно зарегистрированы!' + '\n' + \
                           'Чтобы узнать что умеет бот жми /help.'
        Data.bot.send_message(message.from_user.id, register_message)
        print(answer_bot + register_message + '\n')
        SQLite.welcome(message)
    else:
        end_text = 'Вы уже зарегистрированы!' + '\n' + \
                   'Чтобы узнать что умеет бот жми /help.'
        Data.bot.send_message(message.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


#  Удаление данных о пользователе из БД
@bot.message_handler(commands=['log_out'])
def log_out(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'True':  # Если пользователь присутствует в БД
        log_out_message = 'До новых встреч ' + message.from_user.first_name + '\n' + \
                           'Данные о вашем аккаунте успешно удалены!' + '\n' + \
                           'Чтобы снова воспользоваться функционалом бота жми /register.'
        Data.bot.send_message(message.from_user.id, log_out_message)
        print(answer_bot + log_out_message + '\n')
        SQLite.log_out(message)
    # else:
    #     end_text = 'Вы уже зарегистрированы!' + '\n' + \
    #                'Чтобы узнать что умеет бот жми /help.'
    #     Data.bot.send_message(message.from_user.id, end_text)
    #     print(answer_bot + end_text + '\n')


#  Список доступных команд
@bot.message_handler(commands=['help'])
def help_command(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'True':  # Проверка на наличие юзера в БД
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
        # bot.send_message(message.from_user.id, What_i_can_do.can_help(message), reply_markup=keyboard)
        bot.send_message(message.chat.id, What_i_can_do.can_help(message), reply_markup=keyboard)
        print(answer_bot + What_i_can_do.can_help(message) + '\n')
    else:
        end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться, жми /start'
        bot.send_message(message.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


#  Узнать кто следующий дежурный
@bot.message_handler(commands=['dezhurnyj'])
def dej(message):
    start = time.time()
    print(full_name_user(message) + 'отправил команду ' + message.text)
    list_name = 'Дежурный'
    some_date = Read_file.read_file(list_name)['Date 1']
    some_date2 = Read_file.read_file(list_name)['Date 2']
    meaning = Read_file.read_file(list_name)['Text 3']
    read_type = Read_file.read_file(list_name)['Type']
    difference_date = Read_file.read_file(list_name)['Dif date']

    if SQLite.check_for_existence(message.from_user.id) == 'True':  # Проверка на наличие юзера в БД
        if read_type == 'date':
            if difference_date < 0:  # Если событие в прошлом
                Clear_old_data.clear(list_name)  # Очистить старые данные
                dej(message)  # Перезапустить функцию
            elif difference_date >= 0:  # Если дата уведомления сегодня или в будущем
                text_day = 'В период с ' + str(some_date.strftime("%d.%m.%Y")) + ' по ' + \
                           str(some_date2.strftime("%d.%m.%Y")) + ' '  # Период дежурства
                text_who = 'будет дежурить ' + meaning + '.'  # Имя следующего дежурного
                end_text = str(text_day) + str(text_who)  # Объединяем строки выше в одну
                if meaning == 'Дмитрий @L7kestyle':
                    bot.send_message(message.chat.id, end_text)
                    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEI3dVhbnLM4xnDFJ42hL-Az2Y5wQABuYkAAq8BAAI3hDAAAV3qyNfmaojdIQQ')
                    end = time.time()
                    print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
                elif meaning == 'Павел @Van_leff':
                    bot.send_message(message.chat.id, end_text)
                    bot.send_sticker(message.chat.id,
                                     'CAACAgIAAxkBAAEI3fRhbnjFbLE-As0Kt0fXINgAASCn4g4AAngCAAJWnb0K_LoItZF9HAwhBA')
                    end = time.time()
                    print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
                elif meaning == 'Алексей':
                    bot.send_message(message.chat.id, end_text)
                    bot.send_sticker(message.chat.id,
                                     'CAACAgIAAxkBAAEI3flhbnm-iSTEJPhsWsnCjC9N9ZOkcQACGwEAAp38IwABs3RXktUEV0AhBA')
                    end = time.time()
                    print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
                elif meaning == 'Никита @nikita_it_remit':
                    bot.send_message(message.chat.id, end_text)
                    bot.send_sticker(message.chat.id,
                                     'CAACAgIAAxkBAAEI3f9hbnxmHX2voITw59wxUrnMeZc95AACBQEAAvcCyA_R5XS3RiWkoSEE')
                    end = time.time()
                    print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
                else:
                    bot.send_message(message.chat.id, end_text)
                    end = time.time()
                    print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
        elif read_type == 'incorrect':
            end_text = some_date
        elif read_type == 'none':
            end_text = some_date
            bot.send_message(message.chat.id, text=end_text)
            end = time.time()
            print('Время работы запроса(сек): ' + str(int(end - start)) + '\n')
        else:
            end_text = 'Ошибка чтения данных Dej'
    else:
        end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться, жми /start'
        bot.send_message(message.from_user.id, end_text)
        end = time.time()
        print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')


#  Узнать кто следующий идёт на инвентаризацию
@bot.message_handler(commands=['invent'])
def invent(message):
    start = time.time()
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'True':  # Проверка на наличие юзера в БД
        if SQLite.check_for_admin(message.from_user.id) == 'True':  # Проверка админ ли юзер
            list_name = 'Инвентаризация'  # Получаем имя страницы по ключу
            some_date = Read_file.read_file(list_name)['Date 1']
            meaning2 = Read_file.read_file(list_name)['Text 2']
            read_type = Read_file.read_file(list_name)['Type']
            difference_date = Read_file.read_file(list_name)['Dif date']

            if read_type == 'date':
                Clear_old_data.check_relevance(list_name)

                # Склоняем "день"
                def count_day():
                    dd = ''
                    if difference_date == 0:
                        dd = 'Сегодня инвертаризация.'
                    elif difference_date == 1:
                        dd = 'До предстоящей инвентаризации остался 1 день.'
                    elif 1 < int(difference_date) <= 4:
                        dd = 'До предстоящей инвентаризации осталось ' + str(difference_date) + ' дня.'
                    elif difference_date == 5:
                        dd = 'До предстоящей инвентаризации осталось 5 дней.'
                    elif difference_date > 5:
                        dd = 'Следующая инвентаризация состоится ' + str(some_date.strftime("%d.%m.%Y")) + '.'

                    return dd

                text_day = count_day()  # Кол-во дней до инвентаризации
                text_who = 'Судя по графику, выходит ' + meaning2 + '.'  # Имя следующего дежурного
                end_text = text_day + '\n' + text_who  # Объединяем строки выше в одну
            elif read_type == 'incorrect':
                end_text = str(Read_file.read_file(list_name)['Error'])
            elif read_type == 'none':
                end_text = str(Read_file.read_file(list_name)['Error'])
            else:
                end_text = 'Ошибка чтения данных Invent'

            bot.send_message(message.chat.id, end_text)
            end = time.time()
            print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
        else:
            end_text = 'У вас нет прав для выполнения этой команды'
            bot.send_message(message.chat.id, end_text)
            end = time.time()
            print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')
    else:
        end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться, жми /start'
        bot.send_message(message.from_user.id, end_text)
        end = time.time()
        print(answer_bot + end_text + '\n' + 'Время работы запроса(сек): ' + str(int(end - start)) + '\n')


#  Получить случайное имя из сисадминов
@bot.message_handler(commands=['random'])
def random_name(user_id):
    print(full_name_user(user_id) + 'отправил команду ' + user_id.text)
    if SQLite.check_for_existence(user_id.from_user.id) == 'True':  # Проверка на наличие юзера в БД
        if SQLite.check_for_admin(user_id.from_user.id) == 'True':  # Проверка админ ли юзер
            list_name = ['Паша', 'Дима', 'Никита']
            r_name = random.choice(list_name)
            bot.send_message(user_id.chat.id, text=r_name)
            print(answer_bot + r_name + '\n')
        else:
            text_message = 'У вас нет прав для выполнения этой команды'
            bot.send_message(user_id.from_user.id, text_message)
            print(answer_bot + text_message + '\n')
    else:
        end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться, жми /start'
        bot.send_message(user_id.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


# @bot.message_handler(commands=['set_admin'])
# def set_to_admin(message):
#     print(full_name_user(message) + 'отправил команду ' + message.text)
#     if SQLite.check_for_admin(message.from_user.id) == 'True':
#         text_message = 'Чтобы назначить администратора, перешли мне сообщение от этого человека\n'
#         bot.send_message(message.from_user.id, text=text_message)
#         print(answer_bot + text_message + '\n')
#         bot.register_next_step_handler(message, receive_id)
#     else:
#         text_message = 'У вас нет прав для выполнения этой команды'
#         bot.send_message(message.from_user.id, text_message)
#         print(answer_bot + text_message + '\n')


# def receive_id(message):
#     try:
#         chat_id = message.chat.id
#         id_future_admin = message.forward_from.id
#         first_name_future_admin = str(message.forward_from.first_name)
#         last_name_future_admin = str(message.forward_from.last_name)
#         full_name_future_admin = first_name_future_admin + ' ' + last_name_future_admin
#         print(full_name_user(message) + ' переслал сообщение от пользователя ' + full_name_future_admin +
#               ' содержащее текст:\n' + message.text)
#
#         answer_text = 'Пользователь <' + full_name_future_admin + '> добавлен в список администраторов'
#         msg = bot.send_message(chat_id, answer_text)
#         if SQLite.check_for_existence(id_future_admin) == 'True':
#             bot.register_next_step_handler(msg, SQLite.update_sqlite_table('admin', id_future_admin))
#             print(answer_bot + answer_text + '\n')
#         else:
#             end_text = 'Вы пытаетесь дать админские права пользователю который отсутствует в базе данных!'
#             bot.send_message(chat_id, end_text)
#             print(answer_bot + end_text + '\n')
#     except Exception as e:
#         bot.reply_to(message, 'Что-то пошло не так. Чтобы попробовать снова, жми /set_admin')
#         print(str(e))
#
#     return


# @bot.message_handler(commands=['set_user'])
# def set_to_user(message):
#     print(full_name_user(message) + 'отправил команду ' + message.text)
#     if SQLite.check_for_admin(message.from_user.id) == 'True':
#         text_message = 'Чтобы пользователю присвоить статус <user>, перешли мне сообщение от этого человека\n'
#         bot.send_message(message.from_user.id, text=text_message)
#         print(answer_bot + text_message + '\n')
#         bot.register_next_step_handler(message, receive_id_user)
#     else:
#         text_message = 'У вас нет прав для выполнения этой команды'
#         bot.send_message(message.from_user.id, text_message)
#         print(answer_bot + text_message + '\n')


# def receive_id_user(message):
#     try:
#         chat_id = message.chat.id
#         id_future_user = message.forward_from.id
#         first_name_future_user = str(message.forward_from.first_name)
#         last_name_future_user = str(message.forward_from.last_name)
#         full_name_future_user = first_name_future_user + ' ' + last_name_future_user
#         print(full_name_user(message) + ' переслал сообщение от пользователя ' + full_name_future_user +
#               ' содержащее текст:\n' + message.text)
#
#         answer_text = 'Пользователю <' + full_name_future_user + '> присвоен статус <user>'
#         msg = bot.send_message(chat_id, answer_text)
#         if SQLite.check_for_existence(id_future_user) == 'True':
#             bot.register_next_step_handler(msg, SQLite.update_sqlite_table('user', id_future_user))
#             print(answer_bot + answer_text + '\n')
#         else:
#             end_text = 'Вы пытаетесь присвоить пользователю статус <user>, который отсутствует в базе данных!'
#             bot.send_message(chat_id, end_text)
#             print(answer_bot + end_text + '\n')
#
#     except Exception as e:
#         bot.reply_to(message, 'Что-то пошло не так. Чтобы попробовать снова, жми /set_user')
#         print(str(e))
#     return


@bot.message_handler(commands=['subscribe'])
def set_subscribe(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'True':
        if SQLite.check_for_notification(message.from_user.id) == 'False':
            SQLite.update_sqlite_table('yes', message.from_user.id, 'notification')
            end_text = 'Вы подписаны на уведомления. Теперь вам будут приходить уведомления о том кто дежурит в ' \
                       'выходные, кто в отпуске и прочая информация.\n Чтобы отписаться жми /unsubscribe '
            bot.send_message(message.from_user.id, end_text)
            #  Отсылка уведомлений о действии разработчику
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text=full_name_user(message) + 'подписался на '
                                                                                                    'уведомления.')
            print(answer_bot + end_text + '\n')
        else:
            end_text = 'Вы уже подписаны на уведомления.'
            bot.send_message(message.from_user.id, end_text)
            print(answer_bot + end_text + '\n')
    else:
        end_text = 'Чтобы управлять подпиской нужно зарегистрироваться, жми /start'
        bot.send_message(message.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


@bot.message_handler(commands=['unsubscribe'])
def set_subscribe(message):
    print(full_name_user(message) + 'отправил команду ' + message.text)
    if SQLite.check_for_existence(message.from_user.id) == 'True':
        if SQLite.check_for_notification(message.from_user.id) == 'True':
            SQLite.update_sqlite_table('no', message.from_user.id, 'notification')
            end_text = 'Рассылка отключена.\n Чтобы подписаться жми /subscribe'
            bot.send_message(message.from_user.id, end_text)
            #  Отсылка уведомлений о действии разработчику
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text=full_name_user(message) + 'отписался от '
                                                                                                    'уведомлений.')
            print(answer_bot + end_text + '\n')
        else:
            end_text = 'Нельзя отказаться от уведомлений на которые не подписан.'
            bot.send_message(message.from_user.id, end_text)
            print(answer_bot + end_text + '\n')
    else:
        end_text = 'Чтобы управлять подпиской нужно зарегистрироваться, жми /start'
        bot.send_message(message.from_user.id, end_text)
        print(answer_bot + end_text + '\n')


@bot.message_handler(content_types=['text'])
def other_functions(message):
    print(full_name_user(message) + 'написал: ' + '"' + message.text + '"')
    i_can = "Чтобы узнать что я умею напиши /help."
    bot.send_message(message.chat.id, i_can)
    print(answer_bot + i_can + '\n')


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
            print(str(e))
            # os.kill(os.getpid(), 9)
