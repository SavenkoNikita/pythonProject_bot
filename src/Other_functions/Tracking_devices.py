import datetime
import inspect
import socket
import time
import urllib.request
import xml.etree.ElementTree as ET

from src.Body_bot import Secret
from src.Body_bot.Secret import bot
from src.Other_functions.Functions import SQL, logging_sensors
from ping3 import ping


class TrackingSensor:
    """Мониторинг неисправных датчиков"""

    def __init__(self):
        self.list_controllers = Secret.list_controllers
        self.list_observers = [
            Secret.list_admins.get('Никита'),
        ]
        self.list_names_def_sensor = [
            'Дефростер 1',
            'Дефростер 2',
            'Дефростер 2 низ',
            'Дефростер 3',
            'Деф 1 внутри',
            'Деф 2 внутри',
            'Деф 3 внутри',
            'Деф 1 поверхность',
            'Деф 2 поверхность',
            'Деф 3 поверхность'
        ]

        self.list_names_def_one = [
            'Дефростер 1',
            'Деф 1 внутри',
            'Деф 1 поверхность'
        ]

        self.list_names_def_two = [
            'Дефростер 2',
            'Дефростер 2 низ',
            'Деф 2 внутри',
            'Деф 2 поверхность'
        ]

        self.list_names_def_three = [
            'Дефростер 3',
            'Деф 3 внутри',
            'Деф 3 поверхность'
        ]

        # self.list_observers_defroster = Data.list_observers_defroster

        self.list_observers_defroster = SQL().create_list_users('def', 'yes')

    @property
    def get_data(self):
        """Получить имя контроллера, имя датчика, id датчика и текущие показания температуры. Результат - список с
        вложенными списками [name, value] """

        sensors_with_an_error = []

        for ip_host in self.list_controllers:
            try:
                url = f'http://{ip_host}/values.xml'
                web_file = urllib.request.urlopen(url)
                root_node = ET.parse(web_file).getroot()  # not well-formed (invalid token): line 142, column 7

                device_name = 'Agent/DeviceName'
                sensor_name = 'SenSet/Entry/Name'
                sensor_id = 'SenSet/Entry/ID'
                sensor_value = 'SenSet/Entry/Value'

                name_dev = root_node.find(device_name).text
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
                list_sensor_id = list_data_sensor[1]
                list_sensor_value = list_data_sensor[2]

                count = 0
                number_of_entries = len(list_data_sensor[0])

                while count < number_of_entries:
                    # text = 'Sensor_name: ' + list_sensor_name[count] + \
                    #        '\nID: ' + list_sensor_id[count] + \
                    #        '\nValue: ' + list_sensor_value[count] + '\n'
                    # print(text)

                    sensors_with_an_error.append([list_sensor_name[count], list_sensor_value[count]])

                    id_sensor = list_sensor_id[count]
                    name_sensor = list_sensor_name[count]
                    last_value = list_sensor_value[count]
                    now_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
                    SQL().updating_sensor_data(id_sensor=id_sensor, name_sensor=name_sensor, ip_host=ip_host,
                                               name_host=name_dev, online='True', last_value=last_value,
                                               last_update=now_date)
                    # print(id_sensor, name_sensor, i, name_dev, 'True', last_value, now_date)

                    count += 1
            except OSError:
                text_error = f'Нет соединения с {ip_host}'
                print(text_error)
                SQL().host_sensors_error(ip_host)
                # Data.bot.send_message(Data.list_admins.get('Никита'), OSError)
                logging_sensors('warning', text_error)
                # pass
                continue
            except Exception as error:
                time.sleep(3)

                #  Получить имя модуля в котором сработало исключение
                frm = inspect.trace()[-1]
                file_name = frm[1]
                line_error = frm[2]

                text = (f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                        f'Сработало исключение: "{error}"\n'
                        f'Имя файла: {file_name}\n'
                        f'Строка: {line_error}\n')

                bot.send_message(chat_id=Secret.list_admins.get('Никита'), text=text)
                print(text)

        return sensors_with_an_error

    def check_defroster(self):
        """Формирует список датчиков дефростеров. Результат - список"""

        def_one = []
        def_two = []
        def_three = []

        for name_sensor, value_sensor in self.get_data:
            if name_sensor in self.list_names_def_sensor:
                if int(float(value_sensor)) <= int(float(-100)):
                    text_message = f'"{name_sensor}" : неисправен'
                    if name_sensor in self.list_names_def_one:
                        def_one.append(text_message)
                    elif name_sensor in self.list_names_def_two:
                        def_two.append(text_message)
                    elif name_sensor in self.list_names_def_three:
                        def_three.append(text_message)
                else:
                    text_message = f'"{name_sensor}" : {value_sensor} ℃'
                    if name_sensor in self.list_names_def_one:
                        def_one.append(text_message)
                    elif name_sensor in self.list_names_def_two:
                        def_two.append(text_message)
                    elif name_sensor in self.list_names_def_three:
                        def_three.append(text_message)

        def_one.sort()
        def_two.sort()
        def_three.sort()

        now_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        nl = '\n'
        end_text = f'**Мониторинг дефростеров**\n' \
                   f'{now_date}\n\n' \
                   f'_Первый дефростер_\n' \
                   f'{nl.join(def_one)}\n\n' \
                   f'_Второй дефростер_\n' \
                   f'{nl.join(def_two)}\n\n' \
                   f'_Третий дефростер_\n' \
                   f'{nl.join(def_three)}\n\n'

        return end_text

    def check_all(self):

        sensors_error = []

        for name_sensor, value_sensor in self.get_data:
            if int(float(value_sensor)) <= int(float(-100)):
                text_message = name_sensor
                sensors_error.append(text_message)
                text_error = (f'Неисправен датчик "{name_sensor}". '
                              f'Текущее показание температуры: {int(float(value_sensor))} ℃')
                logging_sensors(condition='error',
                                text_log=text_error)

        if len(sensors_error) != 0:
            sensors_error.sort()
        else:
            text_message = f'Все датчики работают корректно'
            sensors_error.append(text_message)

        now_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        nl = '\n'
        end_text = f'**Мониторинг неисправных датчиков**\n' \
                   f'{now_date}\n\n' \
                   f'_Список неисправных:_\n' \
                   f'{nl.join(sensors_error)}\n\n'

        return end_text

    def get_all_data(self):
        """Получить имя контроллера, имя датчика, id датчика и текущие показания температуры. Результат - список с
        вложенными списками [name, value] """

        list_data_all = []
        for ip_host in self.list_controllers:
            try:
                url = f'http://{ip_host}/values.xml'
                web_file = urllib.request.urlopen(url)
                root_node = ET.parse(web_file).getroot()

                device_name = 'Agent/DeviceName'

                name_dev = root_node.find(device_name).text

                obs = ['ID', 'Value', 'Min', 'Max', 'SenId', 'Hyst']  # noqa

                sensor = {}
                data_dict = {name_dev: sensor}

                for entry in root_node.findall('SenSet/Entry'):
                    list_data = []
                    for elem in entry:
                        if elem.tag == 'Name':
                            name_sensor = elem.text
                            sensor[name_sensor] = list_data
                        elif elem.tag == 'SenId':
                            list_data.append({elem.tag: elem.text[1:]})
                        elif elem.tag in obs:
                            list_data.append({elem.tag: elem.text})

                list_data_all.append(data_dict)
            except OSError:
                text_error = f'Нет соединения с {ip_host}'
                print(text_error)
        return list_data_all

    def test(self):
        list_data = self.get_all_data()
        # obs = ['ID', 'Value', 'Min', 'Max', 'SenId', 'Hyst']  # noqa

        for controller in list_data:
            name_controller = list(controller.keys())[0]
            for sensor in controller:
                data_sensor = controller.get(name_controller)
                for elem in data_sensor:
                    data_sensor.get(elem)


class TrackingCameras:
    """video"""

    def __init__(self):
        self.subnet = [54, 55]

    def ping(self):
        for subnet in self.subnet:
            # address = f'192.168.{subnet}.1-255'

            counter = 1

            job_list = []
            not_job_list = []

            for device in range(1, 255):
                ip_address = f'192.168.{subnet}.{counter}'
                answer = ping(ip_address)

                counter += 1
                if answer is None:
                    not_job_list.append(ip_address)
                else:
                    try:
                        name_device = socket.gethostbyaddr(ip_address)  # (ip_address)[0]
                        print(f'{ip_address} - {name_device}')
                    except Exception:  # noqa
                        print(f'{ip_address}')
                    finally:
                        job_list.append(ip_address)

            print(job_list)
