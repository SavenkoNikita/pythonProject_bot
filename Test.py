import Data
import Other_function
import SQLite

sticker = SQLite.get_user_sticker(Other_function.get_key(Data.user_data, 'Никита'))
Data.bot.send_sticker(Data.list_admins.get('Никита'), sticker)
# Data.bot.send_sticker(Data.list_admins('Никита'), SQLite.get_user_sticker(Other_function.get_key(Data.user_data, 'Никита')))