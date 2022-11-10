import time

import telebot

import Data
import Other_functions
import Test
from Data import bot2


@bot2.message_handler(commands=['testing'])
def choose_a_topic(message):
    dict_topic = Data.dict_topic

    list_topic_name = []
    for keys in dict_topic:
        list_topic_name.append(keys)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [*list_topic_name, 'Начать тестирование позже']
    keyboard.add(*buttons)
    bot2.reply_to(message, 'Выберите тему тестирования', reply_markup=keyboard)
    bot2.register_next_step_handler(message, choose_start)


def choose_start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Начать тестирование', 'Пройти позже']
    keyboard.add(*buttons)
    bot2.send_message(chat_id=message.from_user.id,
                      text=f'Вы выбрали тестирование на тему {message.text}.\n'
                           f'Вам будет задан вопрос и даны варианты ответа. На каждый вопрос отводится 1 минута. '
                           f'По её истечению, появится следующий вопрос. Выберите действие:',
                      reply_markup=keyboard)
    bot2.register_next_step_handler(message, choose, Data.dict_topic[message.text])


def choose(message, code_test):
    if message.text == 'Начать тестирование':
        start_testing(message, code_test)
    elif message.text == 'Пройти позже':
        end_text = 'Операция прервана. Когда будете готовы клик -> /testing'
        bot2.reply_to(message, end_text)
        exit()


def start_testing(message, code_test, count_question=1):
    user_id = message.from_user.id

    dict_data = Test.Employee_testing(user_id).create_text_answer()
    if dict_data is not None:
        text_question = dict_data.get('text_question')
        id_question = dict_data.get('id_question')
        # print(f'Вопрос = {id_question}')
        list_answers = dict_data.get('list_of_response_options')
        list_count = dict_data.get('list_count_key')

        ret = '\n'  # Перенос строки
        text_message = f'Вопрос {count_question}\n\n{text_question}\n\n{f"{ret}{ret}".join(list_answers)}'

        message_text = bot2.send_message(chat_id=user_id,
                                         text=text_message)

        message_poll = bot2.send_poll(chat_id=user_id,
                                      question=text_question,
                                      options=list_count,
                                      type='regular',
                                      is_anonymous=False,
                                      allows_multiple_answers=True,
                                      open_period='60')

        message_text_id = message_text.id
        message_poll_id = message_poll.message_id
        poll_id = message_poll.poll.id

        Other_functions.SQL().update_data_poll('id_poll', poll_id, user_id, code_test, id_question)  # Обновление в БД poll_id
        Other_functions.SQL().update_data_poll('id_message', message_text_id, user_id, code_test, id_question)
        Other_functions.SQL().update_data_poll('id_message_poll', message_poll_id, user_id, code_test, id_question)
        Other_functions.SQL().update_data_poll('id_user_message', message.id, user_id, code_test, id_question)

        count_question += 1

        bot2.register_next_step_handler(message, start_testing, code_test, count_question)
    else:
        bot2.send_message(chat_id=user_id, text='Тестирование окончено')
        data = Other_functions.SQL().create_data_poll(user_id, code_test)
        export_json = Test.Employee_testing(user_id).create_json(data)

        #  Отправка json в 1С
        request = Other_functions.Exchange_with_ERP(
            {'ID': user_id,
             'TEST_DONE': code_test,
             'ANSWER_TEST': str(export_json)}
        ).post_request()

        # print(export_json)
        print(type(str(export_json)))

        # count = 1
        # while request.status_code != 200:
        #     Other_functions.Exchange_with_ERP(
        #         {'ID': user_id, 'TEST_DONE': code_test, 'ANSWER_TEST': export_json}).get_request()
        #     if count < 100:
        #         time.sleep(60)
        #         count += 1
        #         print(count)
        #     else:
        #         break

        #  Удаляем лишние сообщения из переписки
        list_message_id = Other_functions.SQL().get_message_poll_id(user_id, code_test)
        for id_message in list_message_id:
            bot2.delete_message(chat_id=user_id, message_id=id_message)

        #  Тут надо удалить из БД все данные о пройденном пользователем тесте


@bot2.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    poll_id = pollAnswer.poll_id
    user_id = pollAnswer.user.id
    poll_answer = pollAnswer.option_ids
    id_question = Other_functions.SQL().get_value('id_question', user_id, poll_id)
    answers = Test.Employee_testing(user_id).get_id_answers(id_question)

    temp_list = []
    for elem in poll_answer:
        temp_list.append(answers.get(elem + 1))

    id_answers = ', '.join(temp_list)
    Other_functions.SQL().update_data_poll_option_ids('id_answer', id_answers, user_id, poll_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Следующий вопрос']
    keyboard.add(*buttons)
    next_step = bot2.send_message(chat_id=user_id, text='Чтобы продолжить нажмите кнопку ниже', reply_markup=keyboard)
    id_message_next_step = next_step.message_id
    Other_functions.SQL().update_data_poll_option_ids('id_start', id_message_next_step, user_id, poll_id)


if __name__ == '__main__':
    while True:
        bot2.polling(none_stop=True)
