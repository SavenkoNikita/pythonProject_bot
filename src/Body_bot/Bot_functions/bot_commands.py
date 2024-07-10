import random
import time

import telebot

from src.Body_bot import Secret
from src.Other_functions import Working_with_notifications, Functions
from src.Other_functions.File_processing import Working_with_a_file
from src.Other_functions.Functions import SQL, logging_telegram_bot, number_of_events

bot = Secret.bot3


def answer_bot(text_answer):
    print(f'Бот ответил:\n{text_answer}\n')


def can_do_it(x):
    """Перечисляет строка за строкой всё что есть в списке с переводом строки."""

    cd = ('\n'.join(map(str, x)))
    return cd


def creating_list_commands(user_id):
    """Формирует список доступных команд для пользователя в зависимости админ он или нет."""

    heading = f'Вот что я умею:\n'
    check_admin = SQL().check_for_admin(user_id)
    if check_admin is True:  # Если пользователь админ
        list_commands = f'{heading} {can_do_it(Secret.list_command_admin)}'  # Передать полный список доступных команд
    else:  # Если пользователь НЕ админ
        list_commands = f'{heading} {can_do_it(Secret.list_command_user)}'  # Передать список команд доступных юзеру
    return list_commands


def get_time_now():
    time_now = lambda x: time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(x))  # Конвертация даты в читабельный вид
    return time_now


class Bot_commands:
    """"""

    def __init__(self, name_object, data_object):
        self.name_object = name_object
        if name_object == 'Message':
            print(f'its {name_object}')
            self.message = data_object
            self.text = data_object.text
            self.user_id = data_object.from_user.id
            self.user_first_name = data_object.from_user.first_name
            self.user_last_name = data_object.from_user.last_name
            self.username = data_object.from_user.username
            self.date_message = data_object.date
            self.check_admin = SQL().check_for_admin(self.user_id)  # Проверяем является ли пользователь админом
            if data_object.forward_from is not None:  # Если сообщение является пересылаемым
                self.forward_user_id = data_object.forward_from.id  # id человека полученного из пересылаемого сообщения
                self.forward_user_first_name = data_object.forward_from.first_name  # Получаем имя
                self.forward_user_last_name = data_object.forward_from.last_name  # Получаем фамилию
                self.forward_username = data_object.forward_from.username  # Получаем username
        elif name_object == 'CallbackQuery':
            print(f'its {name_object}')
            self.message = data_object.message
            self.text = self.message.text
            self.user_id = data_object.from_user.id
            self.user_first_name = data_object.from_user.first_name
            self.user_last_name = data_object.from_user.last_name
            self.username = data_object.from_user.username
            self.check_admin = SQL().check_for_admin(self.user_id)  # Проверяем является ли пользователь админом

        self.log_file = Secret.way_to_log_telegram_bot
        self.hide_keyboard = telebot.types.ReplyKeyboardRemove()

    def type_user(self):
        print(f'its {self.name_object}')
        print(f'{self.full_name_user} отправил команду:\n{self.text}')

    def full_name_user(self):
        """Принимает на вход сообщение. Возвращает имя пользователя: Администратор/Пользователь + Имя + ID"""

        if self.check_admin is True:
            status_user = 'Администратор '
        else:
            status_user = 'Пользователь '
        name_user = f'{self.user_first_name} (ID: {self.user_id})'  # Получаем имя и id
        pattern = f'{get_time_now()}\n{status_user} {name_user}'  # Итог "дата, /n, статус и имя пользователя"
        # print(status_user)
        # print(name_user)
        return pattern

    def existence(self):
        # self.type_user()
        # print(self.user_id)
        if SQL().check_for_existence(self.user_id) is True:  # Проверка на наличие юзера в БД
            SQL().collect_statistical_information(self.user_id)  # Счётчик активности пользователя
            SQL().update_data_user(self.user_id, self.user_first_name, self.user_last_name, self.username)
            if SQL().check_verify_in_ERP(self.user_id) is True:
                return True
            else:
                verify_error = 'Чтобы воспользоваться функцией необходимо пройти верификацию в 1С -> /verification'
                answer_bot(verify_error)
                return verify_error
        else:
            end_text = 'Чтобы воспользоваться функцией нужно зарегистрироваться -> /start'
            answer_bot(end_text)
            return end_text

    def checking_for_an_administrator(self):
        if self.existence() is True:
            if self.check_admin is True:
                return True
            else:  # Если пользователь не админ, бот сообщит об этом
                end_text = 'У вас нет прав для выполнения этой команды'
                answer_bot(end_text)
                return end_text

    def types_message(self):
        """Имитация нажатия клавиш ботом"""

        # count_text_message = random.randint(3, 7)  # Случайное кол-во секунд будет имитироваться набор текста
        count_text_message = float(int(0.4))

        bot.send_chat_action(self.user_id, action='typing')
        time.sleep(count_text_message)

    def command_start(self):
        """Приветственное сообщение"""

        self.type_user()
        if SQL().check_for_existence(self.user_id) is False:  # Если пользователь отсутствует в БД
            # Приветственное сообщение
            hello_message = f'Добро пожаловать {self.user_first_name}!\n' \
                            f'Это информационный бот IT отдела. Тут можно узнать кто из системных администраторов ' \
                            f'дежурный в ближайшие дни, кто и когда отсутствует и прочая информация.\n' \
                            f'Для того чтобы пользоваться функциями бота, необходимо пройти регистрацию ' \
                            f'нажав /register. Тем самым вы даёте согласие на хранение и обработку данных о вашем ' \
                            f'аккаунте. В базу данных будут занесены следующие сведения:\n' \
                            f'ID: {self.user_id}\n' \
                            f'Имя: {self.user_first_name}\n' \
                            f'Фамилия: {self.user_last_name}\n' \
                            f'Username:  @{self.username}\n'
            self.types_message()
            bot.reply_to(self.message, hello_message)
            print(answer_bot(hello_message))

            callback_data = Functions.pack_in_callback_data('command', 'start')

            keyboard = telebot.types.InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(text='Пройти регистрацию', callback_data=callback_data)
            keyboard.add(button)

            Secret.bot.send_message(chat_id=self.user_id,
                                    text=hello_message,
                                    reply_markup=keyboard)

        else:  # Эта строка появится если уже зарегистрированный пользователь попытается заново пройти регистрацию
            end_text = f'Привет еще раз, {self.user_first_name}\nМы уже знакомы!\n' \
                       f'Список доступных команд тут -> /help'
            self.types_message()
            bot.reply_to(self.message, end_text)
            print(answer_bot(end_text))

    def command_register(self):
        """Регистрация данных о пользователе в БД"""

        self.type_user()
        if SQL().check_for_existence(self.user_id) is False:  # Если пользователь отсутствует в БД
            SQL().db_table_val(self.user_id, self.user_first_name, self.user_last_name, self.username)
            bot.send_message(chat_id=self.user_id, text='Подождите. Сохраняю данные о вас...')
            time.sleep(5)  # Подождать указанное кол-во секунд
            register_message = f'Добро пожаловать {self.user_first_name}!\n' \
                               f'Остался последний шаг. Необходимо пройти верификацию в 1С. ' \
                               f'Для этого нажмите сюда -> /verification.'
            # f'Чтобы узнать, что умеет бот, жми /help.\n' \
            # f'Не забудь подписаться на рассылку, чтобы быть в курсе последних событий, жми /subscribe'
            self.types_message()
            bot.reply_to(self.message, register_message)  # Бот пришлёт уведомление об успешной регистрации
            print(f'{answer_bot}{register_message}\n')
        else:  # Иначе бот уведомит о том что пользователь уже регистрировался
            end_text = f'Вы уже зарегистрированы!\nЧтобы узнать что умеет бот жми /help.'
            self.types_message()
            bot.reply_to(self.message, end_text)
            print(answer_bot(end_text))

    def command_log_out(self):
        """Удаление данных о пользователе из БД"""

        self.type_user()
        if SQL().check_for_existence(self.user_id) is True:  # Если пользователь присутствует в БД
            SQL().log_out(self.user_id)  # Удаление данных из БД
            first_message = 'Подождите...'
            self.types_message()
            bot.reply_to(self.message, first_message)
            log_out_message = f'До новых встреч {self.user_first_name}!\n' \
                              f'Данные о вашем аккаунте успешно удалены!\n' \
                              f'Чтобы снова пользоваться функционалом бота, жми /register.'
            self.types_message()
            bot.reply_to(self.message, log_out_message)  # Прощальное сообщение
            print(answer_bot(log_out_message))
        else:  # Иначе бот уведомит о том что пользователь ещё не регистрировался
            end_text = f'Нельзя удалить данные которых нет :)\nЧтобы это сделать, нужно зарегистрироваться!'
            self.types_message()
            bot.reply_to(self.message, end_text)
            print(answer_bot(end_text))

    def command_help(self):
        """Список доступных команд"""

        if self.existence() is True:  # Проверка на наличие юзера в БД
            keyboard = telebot.types.InlineKeyboardMarkup()  # Вызов кнопки
            keyboard.add(telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/nikita_it_remit'))
            list_commands = creating_list_commands(self.user_id)
            self.types_message()
            # Показ списка доступных команд и кнопки "Написать разработчику"
            bot.reply_to(self.message, list_commands, reply_markup=keyboard)
            print(f'{answer_bot}{list_commands}\n')
        else:  # Если пользователь не зарегистрирован, бот предложит это сделать
            end_message = self.existence()
            self.types_message()
            bot.reply_to(self.message, end_message)
            print(f'{answer_bot}{end_message}\n')

    def command_invent(self):
        """Узнать кто следующий на инвентаризацию"""

        list_name = 'Инвентаризация'  # Имя страницы

        if self.checking_for_an_administrator() is True:
            if Working_with_a_file(list_name).read_file() is not None:
                answer_message = Working_with_a_file(list_name).next_invent()
                sticker = Working_with_a_file(list_name).sticker_next_dej()
                self.types_message()
                bot.reply_to(self.message, answer_message)
                if sticker is not None:
                    bot.send_sticker(self.user_id, sticker)
                print(f'{answer_bot}{answer_message}\n')
            else:
                answer_message = Working_with_a_file(list_name).next_invent()
                self.types_message()
                bot.reply_to(self.message, answer_message)
                print(answer_bot(answer_message))
        else:
            end_text = self.checking_for_an_administrator()
            self.types_message()
            bot.reply_to(self.message, end_text)
            print(answer_bot(end_text))

    def command_random(self):
        """Получить случайное имя из сисадминов"""

        if self.checking_for_an_administrator() is True:
            list_name = ['Паша', 'Дима', 'Никита']  # Список имён
            r_name = random.choice(list_name)  # Получение случайного значения из списка
            self.types_message()
            bot.reply_to(self.message, r_name)  # Отправка сообщения с рандомным именем
            print(answer_bot(r_name))
        else:
            end_text = self.checking_for_an_administrator()
            self.types_message()
            bot.reply_to(self.message, end_text)
            print(answer_bot(end_text))

    def command_set_admin(self):
        """Назначить пользователя админом"""

        if self.checking_for_an_administrator() is True:
            answer_message = 'Чтобы назначить администратора, перешли мне сообщение от этого человека'
            self.types_message()
            bot.reply_to(self.message, answer_message)  # Бот пришлёт выше указанный текст
            print(f'{answer_bot}{answer_message}\n')
            bot.register_next_step_handler(self.message,
                                           self.command_set_admin_step_2)  # Регистрация следующего действия
        else:
            end_text = self.checking_for_an_administrator()
            self.types_message()
            bot.reply_to(self.message, end_text)
            answer_bot(end_text)

    def command_set_admin_step_2(self):
        """Обработка пересланного сообщения"""
        try:
            if self.message.forward_from is not None:
                # Склеиваем данные воедино
                full_name_future_admin = f'{self.forward_user_first_name} {self.forward_user_last_name}'
                print(f'{self.full_name_user()} переслал сообщение от пользователя {full_name_future_admin} '
                      f'содержащее текст:\n {self.text}')
                answer_text = f'Пользователь <{full_name_future_admin}> добавлен в список администраторов'
                if SQL().check_for_existence(self.forward_user_id) is True:  # Проверка на наличие человека в БД
                    if SQL().check_for_admin(self.forward_user_id) is False:  # Проверка админ ли юзер
                        SQL().set_admin(self.forward_user_id)  # Обновляем статус нового админа в БД
                        self.types_message()
                        bot.reply_to(self.message, answer_text)  # Бот уведомляет об этом того кто выполнил запрос
                        answer_bot(answer_text)
                        bot.send_message(self.forward_user_id, f'Администратор <{self.user_id}> '
                                                               f'предоставил вам права администратора')
                        # пользователя, что такой-то юзер, дал ему права админа
                    else:  # Если тот кому предоставляют права уже админ, бот сообщит об ошибке
                        end_text = 'Нельзя пользователю дать права администратора, поскольку он им уже является!'
                        self.types_message()
                        bot.reply_to(self.message, end_text)
                        print(f'{answer_bot}{end_text}\n')
                else:  # Если того кому пытаются дать права нет в БД, бот сообщит об ошибке
                    end_text = 'Вы пытаетесь дать права администратора пользователю который отсутствует в базе данных!'
                    self.types_message()
                    bot.reply_to(self.message, end_text)
                    print(f'{answer_bot}{end_text}\n')
        except Exception as error:  # В любом другом случае бот сообщит об ошибке
            error_text = 'Что-то пошло не так. Чтобы попробовать снова, жми /set_admin'
            self.types_message()
            bot.reply_to(self.message, error_text)
            print(str(error))
            logging_telegram_bot('error', str(error))

        # return

    def command_set_user(self):
        """Лишить пользователя прав администратора"""

        if self.checking_for_an_administrator() is True:
            answer_message = ('• Чтобы пользователю присвоить статус <user>, перешлите мне сообщение от этого '
                              'человека.\n'
                              '• Если хотите отказаться от прав админа, в ответ пришлите сообщение с любым текстом.\n'
                              '• Для отмены операции нажмите "Отмена".')
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ['Отмена']
            keyboard.add(*buttons)
            self.types_message()
            bot.reply_to(self.message, answer_message,
                         reply_markup=keyboard)  # Бот пришлёт выше указанный текст и клавиатуру
            bot.register_next_step_handler(self.message,
                                           self.command_set_user_step_2)  # Регистрация следующего действия
            print(f'{answer_bot}{answer_message}\n')
        else:
            end_text = self.checking_for_an_administrator()
            self.types_message()
            bot.reply_to(self.message, end_text)
            answer_bot(end_text)

    def command_set_user_step_2(self):
        try:
            self.type_user()
            hide_keyboard = telebot.types.ReplyKeyboardRemove()
            if self.text == 'Отмена':
                answer_message = 'Операция прервана.'
                self.types_message()
                bot.reply_to(self, answer_message, reply_markup=hide_keyboard)
            else:
                if SQL().check_for_existence(self.forward_user_id) is True:  # Проверка на наличие человека в БД
                    if SQL().check_for_admin(self.forward_user_id) is True:  # Проверка админ ли юзер
                        full_name_future_user = f'{self.forward_user_first_name} {self.forward_user_last_name}'
                        print(f'{self.full_name_user()} переслал сообщение от пользователя {full_name_future_user} '
                              f'содержащее текст:\n {self.text}')
                        answer_text = f'Пользователю <{full_name_future_user}> присвоен статус <user>'
                        SQL().set_user(self.forward_user_id)  # Обновляем статус нового юзера в БД
                        self.types_message()
                        bot.reply_to(self, answer_text, reply_markup=hide_keyboard)  # Бот уведомляет об этом того кто
                        # выполнил запрос
                        answer_bot(answer_text)
                        text_message = f'Администратор <{self.user_first_name}> лишил вас прав администратора'
                        bot.send_message(chat_id=self.forward_user_id, text=text_message)  # Бот уведомляет нового
                        # юзера, что пользователь <Имя>, лишил его прав админа
                    else:  # Если тот, кого лишают прав админа, уже и так юзер, бот сообщит об ошибке
                        end_text = 'Нельзя пользователю присвоить статус <user> поскольку он им уже является'
                        self.types_message()
                        bot.reply_to(self, end_text, reply_markup=hide_keyboard)
                        answer_bot(end_text)
                else:  # Если того, кого пытаются лишить прав админа, нет в БД, бот сообщит об ошибке
                    end_text = 'Вы пытаетесь присвоить пользователю статус <user>, который отсутствует в базе данных!'
                    self.types_message()
                    bot.reply_to(self, end_text, reply_markup=hide_keyboard)
                    answer_bot(end_text)
        except Exception as error:  # В любом другом случае бот сообщит об ошибке
            error_text = 'Что-то пошло не так. Чтобы попробовать снова, жми /set_user'
            self.types_message()
            bot.reply_to(self.message, error_text)
            print(str(error))
            logging_telegram_bot('error', str(error))

    def command_subscribe(self):
        """Подписка на рассылку"""

        if self.existence() is True:  # Проверка на наличие юзера в БД
            if SQL().check_status_DB(self.user_id, 'notification', 'yes') is False:  # Если пользователь не подписчик
                SQL().change_status_DB(self.user_id, 'notification')  # Присвоить статус <подписан>
                end_text = 'Вы подписаны на уведомления. Теперь вам будут приходить уведомления о том кто дежурит в ' \
                           'выходные, кто в отпуске и прочая информация.\n Чтобы отписаться жми /unsubscribe '
                self.types_message()
                bot.reply_to(self.message, end_text)  # Отправка текста выше
                #  Отсылка уведомлений о действии разработчику
                bot.send_message(chat_id=Secret.list_admins.get('Никита'),
                                 text=f'{self.full_name_user()} подписался на уведомления.')
                answer_bot(end_text)
            else:  # Если подписчик пытается подписаться, то получит ошибку
                end_text = 'Вы уже подписаны на уведомления.'
                self.types_message()
                bot.reply_to(self.message, end_text)
                answer_bot(end_text)
        else:  # Если пользователь не зарегистрирован, бот предложит это сделать
            end_text = self.existence()
            self.types_message()
            bot.reply_to(self.message, end_text)
            answer_bot(end_text)

    def command_unsubscribe(self):
        if self.existence() is True:
            if SQL().check_status_DB(self.user_id, 'notification', 'yes') is True:  # Если пользователь подписчик
                SQL().change_status_DB(self.user_id, 'notification')  # Присвоить в БД статус <не подписан>
                end_text = 'Рассылка отключена.\n Чтобы подписаться жми /subscribe'
                self.types_message()
                bot.reply_to(self.message, end_text)  # Отправка текста выше
                #  Отсылка уведомлений о действии разработчику
                bot.send_message(chat_id=Secret.list_admins.get('Никита'),
                                 text=f'{self.full_name_user()} отписался от уведомлений.')
                answer_bot(end_text)
            else:  # Если не подписчик пытается отписаться, то получит ошибку
                end_text = 'Нельзя отказаться от уведомлений на которые не подписан.'
                self.types_message()
                bot.reply_to(self.message, end_text)
                answer_bot(end_text)
        else:  # Если пользователь не зарегистрирован, бот предложит это сделать
            end_text = self.existence()
            self.types_message()
            bot.reply_to(self.message, end_text)
            answer_bot(end_text)

    def command_change_sticker(self):
        """Присвоить/сменить себе стикер"""

        if self.checking_for_an_administrator() is True:
            answer_message = 'Отправь мне стикер который хочешь привязать в своей учётной записи!'
            self.types_message()
            bot.reply_to(self.message, answer_message)
            bot.register_next_step_handler(self.message,
                                           self.command_change_sticker_step_2)  # Регистрация следующего действия
            answer_bot(answer_message)
        else:  # Если пользователь не зарегистрирован, бот предложит это сделать
            end_text = self.checking_for_an_administrator()
            self.types_message()
            bot.reply_to(self.message, end_text)
            answer_bot(end_text)

    def command_change_sticker_step_2(self):
        print(f'{self.full_name_user()} отправил стикер {self.message.sticker.file_id}')
        SQL().update_sqlite_table(self.message.sticker.file_id, self.user_id, 'sticker')
        end_text = 'Стикер обновлён'
        self.types_message()
        bot.reply_to(self.message, end_text)
        answer_bot(end_text)

    def command_dezhurnyj(self):
        """Узнать кто дежурный"""

        if self.existence() is True:  # Проверка на наличие юзера в БД
            answer_message = 'Что вы хотите получить?'
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ['Имя следующего дежурного', 'Список дежурных']
            keyboard.add(*buttons)
            self.types_message()
            bot.send_message(chat_id=self.user_id, text=answer_message, reply_markup=keyboard)
            bot.register_next_step_handler(message=self.message,
                                           callback=self.command_dezhurnyj_step_2)  # Регистрация следующего действия
            answer_bot(answer_message)
        else:  # Если пользователь не зарегистрирован, бот предложит это сделать
            end_text = self.existence()
            self.types_message()
            bot.send_message(chat_id=self.user_id, text=end_text)
            answer_bot(end_text)

    def command_dezhurnyj_step_2(self, message):
        sheet_name = 'Дежурный'
        try:
            if message.text == 'Имя следующего дежурного':
                answer_message = Working_with_a_file(sheet_name).next_dej()
                user_sticker = Working_with_a_file(sheet_name).sticker_next_dej()
                # Пришлёт сообщение о дежурном
                self.types_message()
                bot.reply_to(message, answer_message, reply_markup=self.hide_keyboard)
                if user_sticker is not None:
                    # Пришлёт стикер этого дежурного
                    bot.send_sticker(self.user_id, user_sticker)
                answer_bot(answer_message)
            elif message.text == 'Список дежурных':
                count_data_list = len(Working_with_a_file(sheet_name).list_dej())
                answer_message = number_of_events(count_data_list)
                self.types_message()
                bot.reply_to(message, answer_message, reply_markup=self.hide_keyboard)
                bot.register_next_step_handler(message, self.command_dezhurnyj_step_3, sheet_name,
                                               count_data_list)  # Регистрация следующего действия
                answer_bot(answer_message)
        except Exception as error:  # В любом другом случае бот сообщит об ошибке
            answer_message = 'Что-то пошло не так. Чтобы попробовать снова, жми /dezhurnyj'
            self.types_message()
            bot.reply_to(self.message, answer_message)
            answer_bot(answer_message)
            print(str(error))
            logging_telegram_bot('error', str(error))

    def command_dezhurnyj_step_3(self, message, sheet_name, count_data_list):
        # self.type_user()
        count = int(message.text)
        try:
            if count <= count_data_list:
                data_list = Working_with_a_file(sheet_name).list_dej()
                Working_with_notifications.repeat_for_list(data_list, self.user_id, count)
            else:
                answer_message = f'Вы запрашиваете {count} записей, а есть только {count_data_list}.\n' \
                                 f'Попробуйте снова - /dezhurnyj'
                # self.types_message()
                bot.reply_to(message, answer_message, reply_markup=self.hide_keyboard)
                answer_bot(answer_message)
        except Exception as error:  # В любом другом случае бот сообщит об ошибке
            answer_message = 'Я не распознал число, попробуйте снова - /dezhurnyj'
            # self.types_message()
            bot.reply_to(self.message, answer_message)
            answer_bot(answer_message)
            print(str(error))
            logging_telegram_bot('error', str(error))

    ######
