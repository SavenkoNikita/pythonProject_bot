import time
import Data
import Other_function

bot = Data.bot


@bot.message_handler(content_types=['text'])
def other_functions(message):
    technical_timeout = 'Ведутся технические работы. Бот временно недоступен :('
    bot.reply_to(message, technical_timeout)
    print(f'Пользователь {message.from_user.first_name} написал:\n{message.text}')


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            text_error = e
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text=f'Бот выдал ошибку: {text_error}')
            print(text_error)
            Other_function.logging_event('error', text_error)
