import time
import Data

bot = Data.bot


@bot.message_handler(content_types=['text'])
def other_functions(message):
    technical_timeout = 'Ведутся технические работы. Бот временно недоступен :('
    mes_id = bot.reply_to(message, technical_timeout)
    print(f'Пользователь {message.from_user.first_name} написал:\n{message.text}')
    print(message.message_id)
    # print(message.message_id + 1)
    time.sleep(3)
    bot.delete_message(message.from_user.id, message_id=mes_id.message_id)


    # bot2.choose(id, 'вопрос', options=['1', '2', '3'], )


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            text_error = e
            bot.send_message(chat_id=Data.list_admins.get('Никита'), text=f'Бот выдал ошибку: {text_error}')
            print(text_error)
            Other_functions.logging_event('error', text_error)

