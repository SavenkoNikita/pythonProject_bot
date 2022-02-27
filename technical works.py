import time
import Data
import Other_function

bot = Data.bot


@bot.message_handler(content_types=['text'])
def other_functions(message):
    technical_timeout = 'Ведутся технические работы. Бот временно недоступен :('
    bot.reply_to(message, technical_timeout)
    print('Пользователь', message.from_user.first_name, 'написал:\n', message.text)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text='Бот выдал ошибку: ' + str(e))
            print(str(e))
            Other_function.logging_event('error', str(e))
