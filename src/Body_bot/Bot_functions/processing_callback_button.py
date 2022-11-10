from Data import bot
from src.Body_bot.Bot_functions.bot_commands import Bot_commands
from src.Other_functions import Menu_bot
from src.Other_functions.Functions import SQL

test_dict_menu = {'Menu': {'name_button': 'callback_data'}}
test_dict_lot = {'Lot': {'lot_number': 2}}
test_dict_functions = {'Functions': {'name_button': 'name_func'}}


class Callback_button:
    """Обработка нажатых клавиш. Принимает словарь, распаковывает, обрабатывает и выполняет нужную функцию"""

    def __init__(self, name_button, value_button, user_id, object_data):
        self.name_button = name_button
        self.value_button = value_button
        # self.dict_data = dict_data
        # self.type_button = [key for key in dict_data.keys()][0]  # 1й ключ из словаря - тип кнопки (меню/команда и тп)
        # self.name_button = [name for name in self.type_button.keys()][0]  # Имя кнопки
        # self.callback_button = dict_data.get(self.name_button)  # callback кнопки
        self.user_id = user_id
        print(self.value_button, self.user_id)
        self.object_data = object_data

    # def type_definition(self):
    #     """В зависимости от типа кнопки, перенаправляет на нужную обработку"""
    #
    #     if self.type_button == 'Menu':
    #         self.menu_processing()
    #     elif self.type_button == 'Lot':
    #         self.lot_processing()
    #     elif self.type_button == 'Functions':
    #         self.functions_processing()

    def menu_processing(self, message_id):
        print(message_id)
        func = SQL().get_name_attr_class_or_insert_button(self.name_button, self.value_button)
        keyboard = eval(func)
        bot.edit_message_text(text=self.name_button,
                              chat_id=self.user_id,
                              message_id=message_id,
                              reply_markup=keyboard)
        # else:
        #     eval(func)
        # if self.value_button == 'home':
        #     text = 'Главное меню'
        #     keyboard = Menu_bot.Bot_menu(self.user_id).main_menu()
        #     return [text, keyboard]
        # elif self.value_button == 'button_main_functions':
        #     text = 'Основные функции'
        #     keyboard = Menu_bot.Bot_menu(self.user_id).main_func()
        #     return [text, keyboard]
        # elif self.value_button == 'button_managing_subscriptions':
        #     text = 'Управление подписками'
        #     keyboard = Menu_bot.Bot_menu(self.user_id).managing_subscriptions()
        #     return [text, keyboard]
        # elif self.value_button == 'button_account_management':
        #     text = 'Настройка аккаунта'
        #     keyboard = Menu_bot.Bot_menu(self.user_id).account_management()
        #     return [text, keyboard]
        # elif self.value_button == 'button_additional_functions':
        #     text = 'Дополнительные функции'
        #     keyboard = Menu_bot.Bot_menu(self.user_id).additional_functions()
        #     return [text, keyboard]
        # elif self.value_button == 'button_dej':
        #     Bot_commands('CallbackQuery', self.object_data).command_dezhurnyj()
        # eval(f'object_test().{param_one}()')
        # else:

    # def lot_processing(self):
    #     print('test')
    #
    # def functions_processing(self):
    #     print('test')
