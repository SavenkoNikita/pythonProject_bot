# import Functions
#
# Functions.File_processing('Дежурный').check_dej_tomorrow()

import Functions
# import Data
#
# message_id = Data.bot.send_message(1827221970, 'Start tracking sensor in defroster').message_id
# message_id = 35181
# # message_id = int(message_id)
# print(message_id)
# print(type(message_id))
#
# Functions.SQL().update_mess_id_by_table_def(1827221970, message_id)

# print(Functions.SQL().get_dict())

# Functions.Notification().update_mess()
# import Tracking_sensor

# Functions.Notification().update_mess('observers_for_faulty_sensors', Tracking_sensor.TrackingSensor().check_all())
# Functions.Notification().update_mess('tracking_sensor_defroster', Tracking_sensor.TrackingSensor().check_defroster())

# Functions.SQL().update_mess_id_by_table(1827221970, message_id, 'observers_for_faulty_sensors', 'observer_all_sensor')

# Functions.File_processing('Уведомления для всех').check_event_today()
# Functions.File_processing('Уведомления для подписчиков').check_event_today()
# Functions.File_processing('Уведомления для админов').check_event_today()

# Functions.File_processing('Дежурный').check_dej_tomorrow()

# print(Functions.SQL().search_not_answer())

# question = 'Здрасьте!'
# answer = 'И вам не хворать!'

# Functions.SQL().update_answer_speak_DB(question, answer)

data_list = Functions.File_processing('Дежурный').read_file()

for i in data_list:
    first_date = i[0].strftime('%d.%m.%Y')  # Дата str(1)
    second_date = i[1].strftime('%d.%m.%Y')  # Дата str(2)
    name_from_SQL = i[2]  # Имя дежурного

    text_message = f'В период с {first_date} по {second_date} будет дежурить {name_from_SQL}.'

    print(text_message)
