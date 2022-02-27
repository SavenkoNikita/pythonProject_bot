import Data
import Other_function

for i in Data.sheets_file:
    print(i)
    print(f'{Other_function.File_processing(i).read_file()}\n\n')
