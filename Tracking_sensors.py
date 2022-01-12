import urllib.request
import xml.etree.ElementTree as ET

import Data
import Other_function


def get_data(url):
    web_file = urllib.request.urlopen(url)
    root_node = ET.parse(web_file).getroot()

    device_name = 'Agent/DeviceName'
    sensor_id = 'SenSet/Entry/ID'
    sensor_name = 'SenSet/Entry/Name'
    sensor_value = 'SenSet/Entry/Value'

    list_sensor_id = []
    list_sensor_name = []
    list_sensor_value = []

    for tag in root_node.findall(device_name):
        name_dev = 'Name device: ' + str(tag.text) + '\n'
        print(name_dev)

    for tag in root_node.findall(sensor_id):
        list_sensor_id.append(tag.text)

    for tag in root_node.findall(sensor_name):
        list_sensor_name.append(tag.text)

    for tag in root_node.findall(sensor_value):
        list_sensor_value.append(tag.text)

    list_data_sensor = [
        list_sensor_id,
        list_sensor_name,
        list_sensor_value
    ]

    count = 0
    number_of_entries = len(list_data_sensor[0])

    while count < number_of_entries:
        text = 'Sensor_name: ' + list_sensor_name[count] + \
               '\nID: ' + list_sensor_id[count] + \
               '\nValue: ' + list_sensor_value[count] + '\n'
        print(text)
        if list_sensor_value[count] == str(-999.9):
            text_message = 'Опрос датчиков:\n' + name_dev + text
            print(text_message)
            Data.bot.send_message(chat_id=Data.list_admins.get('Никита'), text=text_message)
            Other_function.logging_event('warning', text_message)
        count += 1


list_controllers = [
    Data.controller_1,
    Data.controller_2,
    Data.controller_3,
    Data.controller_4,
    Data.controller_5,
    Data.controller_6,
    Data.controller_7,
    Data.controller_8
]


def check_errors_sensor():
    for i in list_controllers:
        try:
            get_data('http://' + i + '/values.xml')
        except OSError:
            text_error = 'Опрос датчиков:\n' + 'Нет соединения с ' + i
            print(text_error)
            Data.bot.send_message(Data.list_admins.get('Никита'), text_error)
            Other_function.logging_event('warning', text_error)
            continue
