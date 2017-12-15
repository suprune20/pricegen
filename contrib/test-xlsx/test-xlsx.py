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

# Так в этом INPUT_FILE. В другом может быть иначе
#
COL_NUMBERS = dict(
    inner_id_col=1,
    partnumber_col=2,
    brand_col=3,
    item_name_col=4,
    price_col=5,
    quantity_col=6,
    delivery_time_col=7
)

# Это будет вычисляться. А здесь затычка (plug)
#
DELIVERY_TYME_PLUG = 120

# Для установки в settings.py
# ---------------------------

OUTPUT_SHEET_NAME = 'TDSheet'

# Параметры колонок.
#
COL_WIDTHS = dict(
    inner_id_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    partnumber_col=dict(
        width=18,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    brand_col=dict(
        width=19,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    item_name_col=dict(
        width=90,
        font=dict(
            name='Arial',
            size=9,
            bold=True,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    price_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='right'
        ),
    ),
    quantity_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='right'
        ),
    ),
    delivery_time_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
)

# -----------

from openpyxl import load_workbook, Workbook

def main():
    input_wb = load_workbook(filename = INPUT_FILE)
    input_sheet = input_wb.active

    output_book = Workbook()
    output_sheet = output_book.active
    output_sheet.title = OUTPUT_SHEET_NAME

    rows = input_sheet.rows
    for row in rows:
        output_row = list()
        for cell in row:
            output_row.append(cell.value)
        output_sheet.append(output_row)

    for i, column_cells in enumerate(input_sheet.columns):
        length = input_sheet.column_dimensions[column_cells[0].column].width
        output_sheet.column_dimensions[column_cells[0].column].width = length

    output_book.save(OUTPUT_FILE)

def as_text(value):
    if value is None:
        return ""
    return str(value)

main()
