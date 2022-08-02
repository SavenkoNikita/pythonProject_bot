import time

from sense_hat import SenseHat
import telebot

import Data

sense = SenseHat()
# sense.show_message("Wake up,Neo")

bot2 = Data.bot2


@bot2.message_handler(content_types=['text'])
def s(message):
    print(f'{message.from_user.first_name}: {message.text}')

    sense.clear()
    sense.set_rotation(180)
    yellow = (255, 255, 0)

    count = 3
    t = 0.3
    while count != 0:
        sense.show_letter(str(count), text_colour=yellow)
        time.sleep(t)
        sense.show_message('')
        sense.clear()
        count -= 1

    sense.show_message(message.text, text_colour=yellow, scroll_speed=0.04)

    # sense.clear()
    #
    # g = (0, 255, 0)
    # b = (0, 0, 0)
    # z = [
    #     b, b, b, b, b, b, b, b,
    #     b, g, g, g, g, g, g, b,
    #     b, b, b, b, b, g, b, b,
    #     b, b, b, b, g, b, b, b,
    #     b, b, b, g, b, b, b, b,
    #     b, b, g, b, b, b, b, b,
    #     b, g, g, g, g, g, g, b,
    #     b, b, b, b, b, b, b, b
    # ]
    #
    # sense.set_pixels(z)


if __name__ == '__main__':
    while True:
        try:
            bot2.polling(none_stop=True)
        except Exception as e:
            print(e)
