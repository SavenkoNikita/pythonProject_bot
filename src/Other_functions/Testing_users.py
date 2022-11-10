import time

import Data

bot2 = Data.bot2


@bot2.message_handler(commands=['start'])
def send_poll(message):
    user_message_id = message.id

    time_period = 5

    first_message = bot2.send_message(chat_id=message.from_user.id,
                                      text='Вам будет задан вопрос и варианты ответа. На каждый вопрос даётся 1 '
                                           'минута. По её истечению придёт следующий вопрос.').message_id

    time.sleep(time_period)

    bot2.delete_message(chat_id=message.from_user.id,
                        message_id=first_message)

    # Получить json с вопросами и ответами
    json = src.Exchange_with_ERP.Exchange_with_ERP.Exchange_with_ERP(
        {Data.number: message.from_user.id, Data.func_name4: '000000002'}).answer_from_ERP()

    if 'TEST_CODE' in json:
        test = json.get('TEST_CODE')
        count_question = 1

        total_list_answers = []

        # Сформированный json для передачи
        output_json = {
            'TEST_CODE': {'IdPoll': json.get('ИдентификаторТемы'),
                          'Answers': total_list_answers,
                          'IdTelegramUser': message.from_user.id}
        }

        for elem in test:
            id_question = elem.get('ИдентификаторВопроса')  # Код вопроса
            dict_id_question = {'IdQuestion': id_question}  # Добавляем в словарь {'IdQuestion': id_вопроса}
            total_list_answers.append(dict_id_question)  # Добавляем в общий список с вопросами и ответами словарь выше

            text_question = elem.get('Вопрос')  # Текст вопроса
            variable_question = elem.get('ВариантыОтветов')  # Текст вариантов ответов

            count = 1

            dict_id_answer = {}
            list_answers = []  # Список вопросов в виде текста
            list_count = []  # [1 вариант, 2 вариант...]

            # Здесь формируется присылаемый текст пользователю
            for variable in variable_question:  # Повторить для каждого варианта ответа
                text_variable_question = ' '.join(variable.get('Ответ').split())  # Текст вопроса
                list_answers.append(f'{count}. {text_variable_question}')  # Формируем список вопросов (текст)
                list_count.append(f'{count} вариант')  # Формируем текст кнопок вариантов ответов в poll

                id_variable_answer = variable.get('ИдентификаторОтвета')  # Код варианта ответа
                dict_id_answer[count] = id_variable_answer  # {номер вопроса: id вопроса}
                dict_id_answers = {}  # Тут будет {'IdAnswers': list(коды ответов)}
                count += 1

            ret = '\n'  # Перенос строки
            text_message = f'Вопрос {count_question}\n\n{text_question}\n\n{f"{ret}{ret}".join(list_answers)}'

            id_message = bot2.send_message(chat_id=message.from_user.id,
                                           text=text_message).message_id

            message_poll = bot2.choose(chat_id=message.from_user.id,
                                       question=text_question,
                                       options=list_count,
                                       type='regular',
                                       is_anonymous=False,
                                       allows_multiple_answers=True,
                                       open_period=time_period)

            id_message_poll = message_poll.id

            @bot2.poll_answer_handler()
            def handle_poll_answer(pollAnswer):
                list_number_answer = pollAnswer.option_ids  # id ответа
                list_id_answers = []  # {id ответа, id ответа...}
                if len(list_number_answer) != 0:
                    for number in list_number_answer:
                        number += 1  # К id ответа +1 чтобы соответствовал цифрам вариантов ответов в тексте
                        if 0 < number <= len(variable_question):
                            answer = dict_id_answer.get(number)  # Достаём из словаря идентификатор ответа
                            # соответствующий номеру нажатой пользователем кнопки
                            list_id_answers.append(answer)  # Добавляем идентификатор ответа в список с ответами
                dict_id_answers['IdAnswers'] = list_id_answers
                total_list_answers.append(dict_id_answers)  # Добавляем в конечный json список

            time.sleep(time_period)

            bot2.delete_message(chat_id=message.from_user.id,
                                message_id=id_message)
            bot2.delete_message(chat_id=message.from_user.id,
                                message_id=id_message_poll)
            count_question += 1

        end_message = bot2.send_message(chat_id=message.from_user.id,
                                        text='Тест завершён').message_id

        time.sleep(time_period)
        bot2.delete_message(chat_id=message.from_user.id,
                            message_id=end_message)
        bot2.delete_message(chat_id=message.from_user.id,
                            message_id=user_message_id)
        print(output_json)
    else:
        print(json)


if __name__ == '__main__':
    while True:
        bot2.polling(none_stop=True)
