import urllib.request
import xml.etree.ElementTree as ET

import Data
import Other_function


# def check_errors_sensor():
#     for i in Data.list_controllers:
#         try:
#             get_data('http://' + i + '/values.xml')
#         except OSError:
#             text_error = 'Опрос датчиков:\n' + 'Нет соединения с ' + i
#             print(text_error)
#             Data.bot.send_message(Data.list_admins.get('Никита'), text_error)
#             Other_function.logging_event('warning', text_error)
#             continue
#
#
# def get_data(url):
#     web_file = urllib.request.urlopen(url)
#     root_node = ET.parse(web_file).getroot()
#
#     device_name = 'Agent/DeviceName'
#     sensor_name = 'SenSet/Entry/Name'
#     sensor_id = 'SenSet/Entry/ID'
#     sensor_value = 'SenSet/Entry/Value'
#
#     name_dev = root_node.find(device_name).text
#     # print(name_dev)
#
#     data_sheets = [
#         sensor_name,
#         sensor_id,
#         sensor_value
#     ]
#
#     list_data_sensor = []
#     for i in data_sheets:
#         for tag in root_node.findall(i):
#             data_list = tag.text
#             list_data_sensor.append(data_list)
#
#     def chunk_using_generators(lst, n):
#         for element in range(0, len(lst), n):
#             yield lst[element:element + n]
#
#     list_data_sensor = list(chunk_using_generators(list_data_sensor, int(len(list_data_sensor) / 3)))
#
#     list_sensor_name = list_data_sensor[0]
#     list_sensor_id = list_data_sensor[1]
#     list_sensor_value = list_data_sensor[2]
#
#     count = 0
#     number_of_entries = len(list_data_sensor[0])
#
#     while count < number_of_entries:
#         text = 'Sensor_name: ' + list_sensor_name[count] + \
#                '\nID: ' + list_sensor_id[count] + \
#                '\nValue: ' + list_sensor_value[count] + '\n'
#         # print(text)
#         if list_sensor_value[count] == str(-999.9):
#             text_message = 'Недоступен датчик:\n' + name_dev + '\n' + text
#             print(text_message)
#             Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_message)
#             Other_function.logging_event('warning', text_message)
#         count += 1


class TrackingSensor:
    """Мониторинг неисправных датчиков"""
    def __init__(self, list_controllers):
        for i in list_controllers:
            try:
                self.url = 'http://' + i + '/values.xml'
                get_data(self.url)
            except OSError:
                text_error = 'Опрос датчиков:\n' + 'Нет соединения с ' + i
                print(text_error)
                Data.bot.send_message(Data.list_admins.get('Никита'), text_error)
                Other_function.logging_event('warning', text_error)
                continue

    def get_data(self, url):
        self.url = url
        web_file = urllib.request.urlopen(url)
        root_node = ET.parse(web_file).getroot()

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
        for i in data_sheets:
            for tag in root_node.findall(i):
                data_list = tag.text
                list_data_sensor.append(data_list)

        def chunk_using_generators(lst, n):
            for element in range(0, len(lst), n):
                yield lst[element:element + n]

        list_data_sensor = list(chunk_using_generators(list_data_sensor, int(len(list_data_sensor) / 3)))

        list_sensor_name = list_data_sensor[0]
        list_sensor_id = list_data_sensor[1]
        list_sensor_value = list_data_sensor[2]

        count = 0
        number_of_entries = len(list_data_sensor[0])

        while count < number_of_entries:
            text = 'Sensor_name: ' + list_sensor_name[count] + \
                   '\nID: ' + list_sensor_id[count] + \
                   '\nValue: ' + list_sensor_value[count] + '\n'
            # print(text)
            if list_sensor_value[count] == str(-999.9):
                text_message = 'Недоступен датчик:\n' + name_dev + '\n' + text
                print(text_message)
                Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_message)
                Other_function.logging_event('warning', text_message)
            count += 1
    # print('finish')