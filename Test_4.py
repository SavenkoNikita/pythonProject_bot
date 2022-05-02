
import Data
# импорт API Telegramm
from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)

# импорт расширений библиотеки
from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    PollHandler,
    MessageHandler,
    Filters,
)

bot2 = Data.bot2


# pollAnswer = []
#
# input_json = {
#     'Как бы вы ответили на вопрос?': {
#         1: 'Первый ответ',
#         2: 'Второй ответ',
#         3: 'Третий ответ',
#         4: 'Четвёртый ответ'
#     }
# }
#
#
# def parse_json(json):
#     pool_values = []
#
#     for key in json.keys():
#         pool_values.append(key)
#
#     for elem in json.values():
#         for k, v in elem.items():
#             pool_values.append(v)
#
#     return pool_values
#
#
# def test(pool_values):
#     answer = pool_values[0]
#
#     first = pool_values[1]
#     second = pool_values[2]
#     third = pool_values[3]
#     fourth = pool_values[4]
#
#     print(f'{answer}\n1.{first}\n2.{second}\n3.{third}\n4.{fourth}')
#
#
# print(parse_json(input_json))
# test(parse_json(input_json))


# @bot2.message_handler(commands=['pool'])
# def pool(message):
#     message_id = (bot2.send_poll(message.chat.id, 'choose one', ['a', 'b', 'c'])).message_id
#     # bot2.stop_poll(message.chat.id, message_id)
#     # payload = answer.pollAnswer.id
#
#     # return payload
#     return message_id
#
#
# @bot2.poll_answer_handler()
# def handle_poll_answer(pool):
#     bot2.stop_poll(pool)
#     # print(pool)
#     print('answer')
#
# if __name__ == '__main__':
#     while True:
#         bot2.polling(none_stop=True)

def start(update, _):
    """Информация о том, что может сделать этот бот"""
    update.message.reply_text(
        'Введите `/poll` для участия в опросе, `/quiz` для участия в викторине или `/preview`'
        ' чтобы создать собственный опрос/викторину'
    )


def poll(update, context):
    """Отправка заранее подготовленного опроса"""
    # Вопрос опроса и его ответы.
    questions = "Как дела?"
    answer = ["Нормально", "Хорошо", "Отлично", "Супер!"]
    # Отправляем опрос в чат
    message = context.bot.send_poll(
        update.effective_chat.id, questions, answer,
        is_anonymous=False, allows_multiple_answers=True,
    )
    # Сохраним информацию опроса в `bot_data` для последующего
    # использования в функции `receive_poll_answer`
    payload = {  # ключом словаря с данными будет `id` опроса
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    # сохранение промежуточных результатов в `bot_data`
    context.bot_data.update(payload)


def receive_poll_answer(update, context):
    """Итоги опроса пользователей"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    except KeyError:  # Это ответ на старый опрос
        return
    selected_options = answer.option_ids
    answer_string = ""
    # подсчет и оформление результатов
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " и "
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} => {answer_string}!",
        parse_mode='HTML',
    )
    # изменение промежуточных результатов в `bot_data`
    context.bot_data[poll_id]["answers"] += 1
    # Закрываем опрос после того, как проголосовали три участника
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def quiz(update, context):
    """Отправка заранее определенную викторину"""
    # Вопрос викторины и ответы
    questions = 'Сколько яиц нужно для торта?'
    answer = ['1', '2', '4', '20']
    # посылаем сообщение с викториной, правильный ответ указывается
    # в `correct_option_id`, представляет собой индекс `answer`
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=2
    )
    # Сохраним промежуточные данные викторины в `bot_data` для использования в `receive_quiz_answer`
    payload = {  # ключом словаря с данными будет `id` викторины
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)


def receive_quiz_answer(update, context):
    """Закрываем викторину после того, как ее прошли три участника"""
    # бот может получать обновления уже закрытого опроса, которые уже не волнуют
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:  # Кол-во участников
        try:
            quiz_data = context.bot_data[update.poll.id]
        except KeyError:  # Это означает, что это ответ из старой викторины
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update, _):
    """Позволяет создать викторину или опрос пользователям чата"""
    # При использовании, без указания типа, позволяет пользователю
    # выбрать то, что он хочет создать - викторину или опрос
    button = [[KeyboardButton("Нажми меня!", request_poll=KeyboardButtonPollType())]]
    message = "Нажмите кнопку, для предварительного просмотра вашего опроса"
    # использование `one_time_keyboard=True` скрывает клавиатуру
    update.effective_message.reply_text(message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True))


def receive_poll(update, _):
    """
        При получении ответа на пользовательский опрос/викторину,
        отвечаем на него закрытым опросом, копируя полученный опрос
    """
    actual_poll = update.effective_message.poll
    # Нужно только `question` и `options`, все остальные
    # параметры не имеют значения для закрытого опроса
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # с `is_closed=True` опрос/викторина немедленно закрывается
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


def help_handler(update, _):
    """Отображение справочного сообщения"""
    update.message.reply_text("Используйте /quiz, /poll или /preview для тестирования этого бота.")


if __name__ == '__main__':
    updater = Updater(Data.TOKEN2)
    dispatcher = updater.dispatcher

    # определяем соответствующие обработчики
    dispatcher.add_handler(CommandHandler('start', start))
    # команда `/pool`
    dispatcher.add_handler(CommandHandler('poll', poll))
    # обработчик ответа на опрос
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    # команда `/quiz`
    dispatcher.add_handler(CommandHandler('quiz', quiz))
    # обработчик ответа на викторину
    dispatcher.add_handler(PollHandler(receive_quiz_answer))
    # команда `/preview`
    dispatcher.add_handler(CommandHandler('preview', preview))
    # обработчик создания пользовательского опроса/викторины
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(CommandHandler('help', help_handler))

    # Запуск бота
    updater.start_polling()
    updater.idle()
