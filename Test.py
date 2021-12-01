import Data
import Other_function
import SQLite

date_list_today = Other_function.read_sheet('Инвентаризация')[1]
event_data = date_list_today[0]

first_date = event_data[0]

event = event_data[1]

a = SQLite.get_user_sticker(Other_function.get_key(Data.user_data, event))
print(a)
print(event)

Data.bot.send_sticker(1827221970, a)
# Data.bot.