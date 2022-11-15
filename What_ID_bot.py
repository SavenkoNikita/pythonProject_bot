import datetime
import time

import requests

import Data
import src.Body_bot.Bot_functions.processing_callback_button
from src.Body_bot.Bot_functions.bot_commands import Bot_commands
from src.Body_bot.Bot_functions.processing_callback_button import Callback_button
from src.Other_functions import Menu_bot
from src.Other_functions.Functions import string_to_dict

bot = Data.bot3


@bot.message_handler(content_types=['photo'])
def get_id_photo(message):
    photo_id = message.photo[0].file_id
    answer_message = f'photo_id изображения - {photo_id}'
    bot.reply_to(message, text=answer_message)
#
#
# @bot.message_handler(content_types=['text'])
# def get_id_user(message):
#     if message.forward_from is None:
#         user_id = message.from_user.id
#         answer_message = f'Ваш user_id - {user_id}'
#     else:
#         user_id = message.forward_from.id
#         answer_message = f'user_id автора сообщения - {user_id}'
#     bot.reply_to(message, text=answer_message)
# @bot.message_handler(commands=['help'])
# def help_command(message):
#     """Список доступных команд"""
#     bot.send_message(message.from_user.id,
#                      text='Главное меню',
#                      reply_markup=Menu_bot.Bot_menu(message.from_user.id).main_menu())
#
#
# @bot.message_handler(content_types=['text'])
# def test(message):
#     print(message.text)
#     print(message.__class__.__name__)
#
#
# @bot.callback_query_handler(func=lambda c: True)
# def inline(c):
#     callback_button = c.data
#     print(callback_button)
#     message_id = c.message.id
#     user_id = c.from_user.id
#     object_data = c
#     name_button = c.message.text
#
#     Callback_button(name_button, callback_button, user_id, object_data).menu_processing(message_id)
#     print(message_id)
    # if text_and_keyboard is not None:
    #     name_button = text_and_keyboard[0]
    #     keyboard = text_and_keyboard[1]
    #     bot.edit_message_text(text=name_button,
    #                           chat_id=user_id,
    #                           message_id=message_id,
    #                           reply_markup=keyboard)

    # if type_button == 'Menu':
    #     bot.edit_message_text(text=name_button,
    #                           chat_id=chat_id,
    #                           message_id=message_id,
    #                           reply_markup=keyboard)
    ### Функции главного меню ###
    # if callback_button == 'home':
    #     bot.edit_message_text(text='Главное меню',
    #                           chat_id=chat_id,
    #                           message_id=message_id,
    #                           reply_markup=Menu_bot.Bot_menu().main_menu())
    # elif callback_button == 'button_main_functions':
    #     bot.edit_message_text(text='Основные функции',
    #                           chat_id=chat_id,
    #                           message_id=message_id,
    #                           reply_markup=Menu_bot.Bot_menu().main_func())
    # elif callback_button == 'button_managing_subscriptions':
    #     bot.edit_message_text(text='Управление подписками',
    #                           chat_id=chat_id,
    #                           message_id=message_id,
    #                           reply_markup=Menu_bot.Bot_menu().managing_subscriptions())
    # elif callback_button == 'button_account_management':
    #     bot.edit_message_text(text='Настройка аккаунта',
    #                           chat_id=chat_id,
    #                           message_id=message_id,
    #                           reply_markup=Menu_bot.Bot_menu().account_management())
    # elif callback_button == 'button_additional_functions':
    #     bot.edit_message_text(text='Дополнительные функции',
    #                           chat_id=chat_id,
    #                           message_id=message_id,
    #                           reply_markup=Menu_bot.Bot_menu().additional_functions())
    ######
    ### Основные функции ###
    # elif callback_button == 'button_dej':
    #     Bot_commands(object_name, object).command_dezhurnyj()


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except requests.exceptions.ReadTimeout:
            time.sleep(3)
            text = f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\nПревышено время ожидания запроса'
            print(text)