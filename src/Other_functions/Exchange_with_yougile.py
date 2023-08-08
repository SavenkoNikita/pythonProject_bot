import http.client

import Data

column_sensors = Data.column_termosensors
column_all_task = Data.column_all_task


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
        'Authorization': f"Bearer {Data.token_yougile}"
    }

    conn.request("POST", "/api-v2/tasks", payload.encode('utf-8'), headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))


def post_task_to_column_sensors(title_text='test', description_text=''):
    """Размещает задачу в колонке 'Термосенсоры'
    с названием {title_text}(если не указать = 'test')
    и описанием {description_text}(если не указать = '')"""

    post_task(title_task=title_text,
              description_text=description_text,
              column_task=column_sensors)
