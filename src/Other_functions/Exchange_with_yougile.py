import http.client
import json

from src.Body_bot import Secret


class YouGile:

    def __init__(self):
        self.column_sensors = Secret.column_termosensors
        self.column_all_task = Secret.column_all_task
        self.connect = http.client.HTTPSConnection("ru.yougile.com")
        self.headers = {
            'Content-Type': "application/json",
            'Authorization': f"Bearer {Secret.token_yougile}",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                              'Chrome/75.0.3770.142 Safari/537.36"
        }

    def post_task(self, title_task='test', description_text='', column_task=''):
        """Создаёт задачу с названием {title_task}(если не указать = 'test'),
        описанием {description_text}(если не указать = ''),
        в колонке {column_task}(если не указать = '')"""

        payload = "{" \
                  f"\n  \"title\": \"{title_task}\"," \
                  f"\n  \"columnId\": \"{column_task}\"," \
                  f"\n  \"description\": \"{description_text}\"" \
                  "}"

        self.connect.request("POST", "/api-v2/tasks", payload.encode('utf-8'), self.headers)

        res = self.connect.getresponse()
        data = res.read()

        response_status = res.status
        if response_status == 201:
            response_text = data.decode("utf-8")
            response_dict = json.loads(response_text)
            id_task_yougile = response_dict.get('id')
            return id_task_yougile
        elif response_status == 429:
            return None

    def get_data_task(self, id_task):
        self.connect.request("GET", f"/api-v2/tasks/{id_task}", headers=self.headers)

        res = self.connect.getresponse()
        data = res.read()
        response_status = res.status
        if response_status == 200:
            response_text = data.decode("utf-8")
            response_dict = json.loads(response_text)
            return response_dict
        else:
            return None

    def delete_task(self, id_task):
        data_task = self.get_data_task(id_task)

        if data_task is not None:
            id_column = data_task.get('columnId')
            status_completed = data_task.get('completed')
            title_task = data_task.get('title')

            if status_completed is False:
                payload = ('{\n  \"deleted\": true,\n  '
                           f'\"columnId\": \"{id_column}\"'
                           '}')

                self.connect.request("PUT", f"/api-v2/tasks/{id_task}", payload, self.headers)

                res = self.connect.getresponse()
                response_status = res.status
                if response_status == 200:
                    print(f'Задача {title_task} с ID {id_task} удалена')
