import time

import Data


def test():
    list_queue = [
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=1),
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=2),
        Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=3)
    ]

    i = 0
    while i < len(list_queue):
        list_queue[i]
        print(list_queue[i])
        # Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=)
        if i == len(list_queue):
            pass
        else:
            time.sleep(5)  # Задержка в секундах
            i += 1


test()
