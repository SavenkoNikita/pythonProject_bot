import http.client
import json

from src.Body_bot import Secret

column_sensors = Secret.column_termosensors
column_all_task = Secret.column_all_task


def post_task(title_task='test', description_text='', column_task=column_all_task):
    """Создаёт задачу с названием {title_task}(если не указать = 'test'),
    описанием {description_text}(если не указать = ''),
    в колонке {column_task}(если не указать, попадёт в колонку 'Задачи общее')"""

    conn = http.client.HTTPSConnection("ru.yougile.com")

    payload = "{" \
              f"\n  \"title\": \"{title_task}\"," \
              f"\n  \"columnId\": \"{column_task}\"," \
              f"\n  \"description\": \"{description_text}\"," \
              "\n  \"archived\": false," \
              "\n  \"completed\": false\n" \
              "}"

    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {Secret.token_yougile}"
    }

    conn.request("POST", "/api-v2/tasks", payload.encode('utf-8'), headers)

    res = conn.getresponse()
    data = res.read()

    response_status = res.status
    if response_status == 201:
        response_text = data.decode("utf-8")
        response_dict = eval(response_text)
        id_task_yougile = response_dict.get('id')
        # print(id_task_yougile)
        return id_task_yougile

    print(f'Response yougile: {data.decode("utf-8")}')


def post_task_to_column_sensors(title_text='test', description_text=''):
    """Размещает задачу в колонке 'Термосенсоры'
    с названием {title_text}(если не указать = 'test')
    и описанием {description_text}(если не указать = '')"""  # noqa

    id_task_yougile = post_task(title_task=title_text,
                                description_text=description_text,
                                column_task=column_sensors)

    return id_task_yougile


# post_task_to_column_sensors('Test')

def get_data_task(id_task):
    conn = http.client.HTTPSConnection("ru.yougile.com")

    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer PrmRWeX6TvHKAyKeBz+G5gCfF-PdaWBa22Vu23HbhDTaoLxOZymxjIgzfRza1D9t"
    }

    conn.request("GET", f"/api-v2/tasks/{id_task}", headers=headers)

    res = conn.getresponse()
    data = res.read()
    response_status = res.status
    if response_status == 200:
        response_text = data.decode("utf-8")
        response_dict = json.loads(response_text)
        print(response_dict)
        return response_dict
    else:
        # print(f'Task not found')
        return None


def delete_task(id_task):
    data_task = get_data_task(id_task)

    if data_task is not None:
        id_column = data_task.get('columnId')
        status_completed = data_task.get('completed')
        title_task = data_task.get('title')

        # print(id_column, status_completed)

        if status_completed is False:
            conn = http.client.HTTPSConnection("ru.yougile.com")

            payload = ('{\n  \"deleted\": true,\n  '
                       f'\"columnId\": \"{id_column}\"'
                       '}')

            headers = {
                'Content-Type': "application/json",
                'Authorization': "Bearer PrmRWeX6TvHKAyKeBz+G5gCfF-PdaWBa22Vu23HbhDTaoLxOZymxjIgzfRza1D9t"
            }

            conn.request("PUT", f"/api-v2/tasks/{id_task}", payload, headers)

            res = conn.getresponse()
            data = res.read()

            print(data.decode("utf-8"))
            response_status = res.status
            if response_status == 200:
                print(f'Задача {title_task} с ID {id_task} удалена')
