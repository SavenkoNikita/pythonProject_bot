import requests
from requests.auth import HTTPBasicAuth
from src.Body_bot import Secret


class Exchange_with_ERP:
    """Позволяет получить некоторые данные из 1С"""

    def __init__(self, params):
        self.request_get = Secret.way_erp_get
        self.request_post = Secret.way_erp_post
        self.login = Secret.login_erp
        self.password = Secret.pass_erp
        self.user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                              'Chrome/75.0.3770.142 Safari/537.36'
        # self.headers = {'Cache-Control': 'private',
        #                 'Content-Type': 'text/html; charset=utf-8',
        #                 'Server': 'Microsoft-IIS/8.5',
        #                 'Date': 'Wed, 01 Jun 2022 09:01:41 GMT',
        #                 'Content-Length': '6908'}
        self.params = params
        # self.key_params = self.params.get.key
        self.response = self.get_request()

    def get_request(self):
        request = requests.get(url=f'{self.request_get}',
                               headers={'User-Agent': self.user_agent_val},
                               auth=HTTPBasicAuth(self.login, self.password),
                               params=self.params)

        return request

    def answer_from_ERP(self):
        try:
            # print(self.response.json())
            # if self.response.status_code == 200:
            if self.response.ok:
                if Secret.func_name1 in self.response.json():
                    return self.in_out()
                elif Secret.func_name2 in self.response.json():
                    return self.get_count_days()
                elif Secret.func_name3 in self.response.json():
                    return self.verification()
                elif Secret.func_name4 in self.response.json():
                    return self.response.json()
            elif self.response.status_code == 400:
                json = self.response.json()
                value = json['ID_Telegram']
                print(value)
                return value
            elif self.response.status_code == 500:
                update_text = f'Не удалось выполнить запрос, возникла ошибка. Сервер 1С недоступен. ' \
                              f'Производится обновление. Повторите попытку позже. ' \
                              f'Status_code: {self.response.status_code}'
                return update_text
        except Exception:
            # print(self.response.status_code)
            # print(self.response.text)
            exception_text = 'Не удалось выполнить запрос, возникла ошибка. Сервер 1С недоступен. ' \
                             'Возможно производится обновление. Повторите попытку позже.'
            return exception_text

    def get_count_days(self):
        """На вход принимает user_id, запрашивает данные из 1С, и возвращает кол-во накопленных дней отпуска.
        Если пользователь не уволен, функция вернёт число, во всех остальных случаях 1С вернёт ошибку"""

        json = self.response.json()
        count_day = int(json[Secret.func_name2])

        return count_day

    def verification(self):
        """Запрос принимает user_id и ИНН пользователя. В случае успеха, обновляет ID Telegram в 1С у пользователя с
        указанным ИНН. Либо возвращает str(ошибку)."""

        json = self.response.json()
        answer_erp = json[Secret.func_name3]

        return answer_erp

    def in_out(self):
        """Хз что делает"""

        json = self.response.json()
        data_list = []
        for value in json.values():
            for elem in value:
                time_in = elem['Время']
                in_out = elem['Вход']
                string_name = f'{time_in} {in_out}'
                data_list.append(string_name)

        return data_list

    def post_request(self):
        request = requests.post(url=self.request_post,
                                headers={'User-Agent': self.user_agent_val},
                                params=self.params,
                                auth=HTTPBasicAuth(self.login, self.password))

        # (url=self.request_post,
        # headers={'User-Agent': self.user_agent_val},
        # auth=HTTPBasicAuth(self.login, self.password),
        # json=json_data)
        # headers=self.headers)

        return request
