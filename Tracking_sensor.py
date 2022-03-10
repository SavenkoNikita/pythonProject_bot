import time
import urllib.request
import xml.etree.ElementTree as ET

import Data
import Other_function


class TrackingSensor:
    """Мониторинг неисправных датчиков"""

    def __init__(self):
        self.list_controllers = Data.list_controllers
        self.list_observers = [
            Data.list_admins.get('Никита'),
        ]
        self.list_names_def_sensor = [
            'Дефростер 1',
            'Дефростер 2',
            'Дефростер 3',
            'Деф 1 внутри',
            'Деф 2 внутри',
            'Деф 3 внутри',
            'Деф 1 поверхность',
            'Деф 2 поверхность',
            'Деф 3 поверхность'
        ]
        self.list_observers_defroster = Data.list_observers_defroster

    @property
    def get_data(self):
        """Получить имя контроллера, имя датчика, id датчика и текущие показания температуры"""

        sensors_with_an_error = []

        for i in self.list_controllers:
            try:
                url = f'http://{i}/values.xml'
                web_file = urllib.request.urlopen(url)
                root_node = ET.parse(web_file).getroot()

                # device_name = 'Agent/DeviceName'
                sensor_name = 'SenSet/Entry/Name'
                sensor_id = 'SenSet/Entry/ID'
                sensor_value = 'SenSet/Entry/Value'

                # name_dev = root_node.find(device_name).text
                # print(name_dev)

                data_sheets = [
                    sensor_name,
                    sensor_id,
                    sensor_value
                ]

                list_data_sensor = []
                for element in data_sheets:
                    for tag in root_node.findall(element):
                        data_list = tag.text
                        list_data_sensor.append(data_list)

                def chunk_using_generators(lst, n):
                    for elem in range(0, len(lst), n):
                        yield lst[elem:elem + n]

                list_data_sensor = list(chunk_using_generators(list_data_sensor, int(len(list_data_sensor) / 3)))

                list_sensor_name = list_data_sensor[0]
                # list_sensor_id = list_data_sensor[1]
                list_sensor_value = list_data_sensor[2]

                count = 0
                number_of_entries = len(list_data_sensor[0])

                while count < number_of_entries:
                    # text = 'Sensor_name: ' + list_sensor_name[count] + \
                    #        '\nID: ' + list_sensor_id[count] + \
                    #        '\nValue: ' + list_sensor_value[count] + '\n'
                    # print(text)

                    sensors_with_an_error.append([list_sensor_name[count], list_sensor_value[count]])

                    count += 1
            except OSError:
                # text_error = f'Нет соединения с {i}'
                print(OSError)
                Data.bot.send_message(Data.list_admins.get('Никита'), OSError)
                Other_function.logging_event('warning', OSError)
                pass

        return sensors_with_an_error

    def check(self):
        """Если есть неисправные датчики, формируется список"""

        list_errors = []
        list_id = []
        while True:
            for name, value in self.get_data:
                if name not in list_errors and value == '-999.9':
                    list_errors.append(name)
                    text_message = f'Датчик <{name}> не работает'
                    print(text_message)

                    for user_id in self.list_observers:
                        not_job = Data.bot.send_message(chat_id=user_id, text=text_message)
                        list_id.append(not_job.message_id)

                    if name in self.list_names_def_sensor:
                        for user_id in self.list_observers_defroster:
                            Data.bot.send_message(chat_id=user_id, text=text_message)

                elif name in list_errors and value != '-999.9':
                    list_errors.remove(name)
                    text_message = f'Работа датчика <{name}> восстановлена.\nТекущее показание температуры <{value}C>.'
                    print(text_message)

                    for user_id in self.list_observers:
                        job = Data.bot.send_message(chat_id=user_id, text=text_message)
                        list_id.append(job.message_id)

                    if name in self.list_names_def_sensor:
                        for user_id in self.list_observers_defroster:
                            Data.bot.send_message(chat_id=user_id, text=text_message)

            time.sleep(300)

            for user_id in self.list_observers:
                if len(list_id) != 0:
                    for id_message in list_id:
                        Data.bot.delete_message(chat_id=user_id, message_id=id_message)
                        list_id.remove(id_message)


TrackingSensor().check()
