#! /usr/bin/env python3

# test read/write xlsx
#
# Моделируем чтение xlsx файла и запись в него

# Запуск из ./manage.py shell:
#   exec(open('/path/to/test-xlsx.py').read())

# Колонки, ширины c пробного прайс-листа, начиная с 1
# при шрифте Arial 9
#
# 1 11.6640625      (inner_id_col)
# 2 17.5            (partnumber_col)
# 3 18.6640625      (brand_col)
# 4 88.1640625      (item_name_col)
# 5 11.33203125     (price_col)
# 6 10.6640625      (quantity_col)

INPUT_FILE = '/home/suprune20/musor/test-xlsx/zzap_p30.xlsx'
OUTPUT_FILE = '/home/suprune20/musor/test-xlsx/output.xlsx'

# Так в этих INPUT_FILE, OUTPUT_FILES. В других может быть иначе.
# Как надо, берется из базы или из settings.
#

from django.conf import settings

input_col_numbers = dict()
for item in settings.XLSX_COL_NUMBERS_DEFAULT:
    if item not in settings.XLSX_OUTPUT_ONLY_COLS:
        input_col_numbers[item] = settings.XLSX_COL_NUMBERS_DEFAULT[item]

output_col_numbers = dict(
    inner_id_col=3,
    partnumber_col=4,
    brand_col=1,
    item_name_col=2,
    price_col=7,
    quantity_col=6,
    delivery_time_col=5
)

# Это будет вычисляться. А здесь затычка (plug)
#
DELIVERY_TYME_PLUG = 130

# -----------

from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment

def main():
    input_wb = load_workbook(filename = INPUT_FILE)
    input_sheet = input_wb.active

    output_book = Workbook()
    output_sheet = output_book.active
    output_sheet.title = settings.XLSX_OUTPUT_SHEET_NAME

    # В базе данных номера колонок начинаются с 1.
    # Приведем эти номера к "машинному виду, т.е. с нуля
    #
    # Заодно получим число колонок в файлах:
    #
    input_sheet_rows = 0
    output_sheet_rows = 0
    
    for item in input_col_numbers:
        input_sheet_rows = max(input_sheet_rows, input_col_numbers[item])
        input_col_numbers[item] -=1
    for item in output_col_numbers:
        output_sheet_rows = max(output_sheet_rows, output_col_numbers[item])
        output_col_numbers[item] -=1
    
    # Теперь список соответствий
    # 0 (inner_id_col in input) : 2 (inner_id_col in output)
    # 1 (partnumber_col in input) : 3 (partnumber_col in output)
    # ...
    #
    map_col_number = [None for i in range(output_sheet_rows)]
    for item in input_col_numbers:
        map_col_number[input_col_numbers[item]] = output_col_numbers[item]

    rows = input_sheet.rows
    n_rows = 0
    for row in rows:
        n_rows += 1
        input_row = ['' for i in range(max(input_sheet_rows ,output_sheet_rows))]
        for i, cell in enumerate(row):
            input_row[i] = cell.value
        output_row = ['' for i in range(output_sheet_rows)]
        output_row[output_col_numbers['delivery_time_col']] = time_human(DELIVERY_TYME_PLUG)
        for i_input, i_output in enumerate(map_col_number):
            if i_output is None:
                # delivery_time_col, уже занесли
                pass
            else:
                output_row[i_output] = input_row[i_input]
        output_sheet.append(output_row)

    # Список соответствий
    # 0-я колонка Excel- файла : 'brand_col'
    # 1-я колонка Excel- файла : 'item_name_col'
    #
    map_output = dict()
    for item in output_col_numbers:
        map_output[output_col_numbers[item]] = item
    for i, column_cells in enumerate(output_sheet.columns):
        try:
            item = map_output[i]
        except KeyError:
            continue
        width = settings.XLSX_COL_STYLES[item]['width']
        font = Font(**settings.XLSX_COL_STYLES[item]['font'])
        alignment = Alignment(**settings.XLSX_COL_STYLES[item]['alignment'])
        output_sheet.column_dimensions[column_cells[0].column].width = width
        
        # А это по всей колонке не задашь! Для LibreOffice так можно,
        # а вот чтоб Microsoft Excel воспринимал, надо устанавливать
        # font, alignment по каждой ячейке из колонки
        #
        for n_row in range(n_rows):
            column_cells[n_row].font = font
            column_cells[n_row].alignment = alignment

    #a1 = output_sheet['A1']
    #a1.font = Font(name='Arial', size=9, bold=True)
    output_book.save(OUTPUT_FILE)

def time_human(mins):
    """
    Время из минут в '?? час. ?? мин.'
    """
    mins_ = mins % 60
    hours_ = int(mins / 60)
    result = ''
    if hours_:
        result += '%s час.' % hours_
    if mins_ and hours_:
        result += ' '
    if mins_:
        result += '%s мин.' % mins_
    return result

main()
