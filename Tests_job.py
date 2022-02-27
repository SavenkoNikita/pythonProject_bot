# import datetime
#
# import Other_function
#
#
# class Tests:
#     def __init__(self, class_name, function_name):
#         self.successful_test = f'Тест {class_name.function_name.__qualname__} пройден УСПЕШНО!'
#         self.fail_test = f'Тест {class_name.function_name.__qualname__} НЕ пройден.'
#         self.sheet_name = 'Дежурный'
#
#     def test_1(self):
#         date_today = datetime.datetime.now()
#         date_two = date_today - datetime.timedelta(days=50)
#         date_string = '01.01.2000'
#         date_none = None
#
#         meaning_list = [
#             date_today,
#             date_two,
#             date_string,
#             date_none
#         ]
#
#         for i in meaning_list:
#             try:
#                 Other_function.File_processing(self.sheet_name).difference_date(i)
#             except:
#                 print(self.fail_test)
#
#
# Tests('File_processing', 'difference_date').test_1()
