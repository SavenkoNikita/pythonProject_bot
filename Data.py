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


name_sticker = {
    'Дмитрий @L7kestyle': 'CAACAgIAAxkBAAEI3dVhbnLM4xnDFJ42hL-Az2Y5wQABuYkAAq8BAAI3hDAAAV3qyNfmaojdIQQ',
    'Павел @Van_leff': 'CAACAgIAAxkBAAEI3fRhbnjFbLE-As0Kt0fXINgAASCn4g4AAngCAAJWnb0K_LoItZF9HAwhBA',
    'Алексей': 'CAACAgIAAxkBAAEI3flhbnm-iSTEJPhsWsnCjC9N9ZOkcQACGwEAAp38IwABs3RXktUEV0AhBA',
    'Никита @nikita_it_remit': 'CAACAgIAAxkBAAEI3f9hbnxmHX2voITw59wxUrnMeZc95AACBQEAAvcCyA_R5XS3RiWkoSEE'
}


user_data = {
    1827221970: ['Никита', 'Никитка', 'Микитко', 'Никуся', 'Никша', 'Микитонько', 'Никиха', 'Микаш', 'Кеня',
                 'Микиточко', 'Ника', 'Никица', 'Никиша', 'Микешка', 'Кита', 'Микусь', 'Никуша', 'Микей', 'Никеня',
                 'Нико', 'Никеша', 'Ники', 'Кеша', 'Мицька', 'Микитка'],
    463376780: ['Дима', 'Димон', 'Дмитрий', 'Димитрий', 'Деметрий', 'Дима', 'Димаха', 'Димаша', 'Димуха', 'Димуша',
                'Димуля', 'Димуся', 'Митя', 'Митяй', 'Митюля', 'Митуля', 'Митюня', 'Митюха', 'Митюша', 'Митяха',
                'Митяша', 'Митря', 'Митра', 'Митраша', 'Митрюха', 'Митрюша', 'Димас', 'Демон'],
    762058672: ['Паша', 'Павел', 'Павелка', 'Павлик', 'Павлуня', 'Павлюня', 'Павлуся', 'Павлюся', 'Павлуха', 'Павлуша',
                'Павля', 'Павлюка', 'Павлюкаша', 'Павша', 'Пава', 'Паха', 'Пашата', 'Пашуня', 'Пашута', 'Пашуха',
                'Паня', 'Пана', 'Панюта', 'Панюха', 'Панюша', 'Паняша', 'Паля', 'Палюня', 'Палуня'],
    1350324635: ['Лёха', 'Алексей', 'Алексейка', 'Алёха', 'Алёша', 'Лёша', 'Али', 'Алик', 'Лёля', 'Аля', 'Алюня',
                 'Люня', 'Лексейка', 'Лекса', 'Лекся', 'Лёкса', 'Лёкся', 'Алёня', 'Лёня', 'Алёка', 'Алека', 'Лёка',
                 'Лека']
}


