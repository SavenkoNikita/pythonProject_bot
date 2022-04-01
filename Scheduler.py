import time
import traceback

import schedule

import Data
import Functions
from Functions import random_name

# Проверяет и уведомляет есть ли завтра дежурный
schedule.every().day.at('15:00').do(Functions.File_processing('Дежурный').check_dej_tomorrow)

# Если инвент вот-вот начнётся, придёт уведомление
schedule.every().day.at('07:00').do(Functions.File_processing('Инвентаризация').check_event_today())

# Проверяет есть ли сегодня уведомления для подписчиков и отправляет их
schedule.every().day.at('08:00').do(Functions.File_processing('Уведомления для подписчиков').check_event_today())

# Проверяет есть ли сегодня уведомления для всех и отправляет их
schedule.every().day.at('08:01').do(Functions.File_processing('Уведомления для всех').check_event_today())

# Проверяет есть ли сегодня уведомления для админов и отправляет их
schedule.every().day.at('08:02').do(Functions.File_processing('Уведомления для админов').check_event_today())

# Присылает случайное имя кто идёт в цех
schedule.every().day.at('08:03').do(random_name)

# Обновляет сообщение у пользователей которые отслеживают дефростеры
schedule.every(1).minutes.do(Functions.Notification().update_mess_def)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception:
        text_error = traceback.format_exc()
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_error)
        print(text_error)
        Functions.logging_event('error', text_error)
