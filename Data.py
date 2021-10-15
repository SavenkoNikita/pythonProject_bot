import telebot

TOKEN = '1013175932:AAGIDc3GACkwXPGK8XRLfJkNQhO_J4xtflw'  # токен бота
bot = telebot.TeleBot(TOKEN)

# Словарь администраторов
list_admins = {
    'Никита': 1827221970,
    'Дима': 463376780,
    'Паша': 762058672,
    'Лёха': 1350324635
}

# Словарь групп
list_groups = {
    'IT_info': -1001332331366,
    'GateKeepers': -1001450700256
}

# Путь к файлу 'Графики дежурств'
host_name = 'R_777'
pass_log_in = '109225081'
way = '192.168.0.236/public_files/14_Отдел_ИТ/1_Личные_папки/Савенко_Никита/Документы/Уведомления в телеграм.xlsx'
route = 'smb://' + host_name + ':' + pass_log_in + '@' + way

# Листы в файле
sheets_file = [
    'Дежурный',
    'Инвентаризация',
    'Уведомления для подписчиков',
    'Уведомления для всех',
    'Уведомления для админов'
]

# Путь к базе данных
way_sql = '/home/nik/Рабочий стол/Проекты python/Data_users_telegram_bot.db'

