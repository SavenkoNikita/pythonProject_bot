from telebot import types


class Bot_menu:
    """Меню бота"""

    def __init__(self):
        self.markup = types.InlineKeyboardMarkup()

        self.list_main_menu = [
            ['Основные функции', 'button_main_functions'],
            ['Управление подписками', 'button_managing_subscriptions'],
            ['Настройка аккаунта', 'button_account_management'],
            ['Дополнительные функции', 'button_additional_functions']
        ]

        self.list_main_functions = [
            ['Узнать кто дежурный', 'button_dej'],
            ['Инвентаризация', 'button_invent'],
            ['Дать пользователю права админа', 'button_admin'],
            ['Лишить пользователя прав админа', 'button_user'],
            ['Создать уведомление', 'button_create_notif']
        ]

        self.list_managing_subscriptions = [
            ['Подписаться на рассылку уведомлений', 'button_subscribe'],
            ['Отказаться от рассылки уведомлений', 'button_unsubscribe'],
            ['Мониторинг дефростеров', 'button_defrosters'],
            ['Мониторинг неисправных датчиков', 'button_all_sensor']
        ]

        self.list_account_management = [
            ['Покинуть чат', 'button_log_out'],
            ['Сменить стикер аккаунта', 'button_sticker']
        ]

        self.list_additional_functions = [
            ['Обратная связь', 'button_feed_back'],
            ['Игры', 'button_games'],
            ['Получить случайное имя', 'button_random'],
            ['Получить список всех пользователей', 'button_all_users']
        ]

    def init_menu(self, data_list_buttons):
        temporary_list = []
        for i in data_list_buttons:
            temporary_list.append(types.InlineKeyboardButton(text=i[0], callback_data=i[1]))

        for elem in temporary_list:
            self.markup.add(elem)

        return self.markup

    def step_back(self, name_button):
        back = types.InlineKeyboardButton(text='<< назад', callback_data=name_button)

        return back

    def home(self):
        home = types.InlineKeyboardButton(text='<<< на главную', callback_data='home')

        return home

    def main_menu(self):
        keyboard = self.init_menu(self.list_main_menu)

        return keyboard

    def lvl_2(self, list_function):
        keyboard = self.init_menu(list_function)
        keyboard.add(self.home())

        return keyboard

    def lvl_3(self, list_function, name_button):
        keyboard = self.init_menu(list_function)
        keyboard.add(self.step_back(name_button))
        keyboard.add(self.home())

        return keyboard
