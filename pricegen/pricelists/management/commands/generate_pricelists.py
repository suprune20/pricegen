# ! /usr/bin/env python3
#
# generate_pricelists.py
#

# Параметр: корневой каталог, внутри которого кладутся pricelists
# и где формируются результаты
#
#   -   Пусть корневой каталог pricege
#   -   имеются организация-продавец korona, у нее точки выдачи
#       * korona pickpoints: zamok, kurasovschina
#   -   поставщики krynka, myasokombinat
#
# Тогда каталог будет выглядеть:
#
# ...pricegen/                                                         (1)
#           korona/
#               suppliers/                                          (2)
#                   /krynka/
#                       some_name1.xlsx (входящий файл)
#                       some_name2.xlsx (входящий файл)
#                   /myasokombinat/
#                       some_name3.xlsx (входящий файл)
#                       some_name4.xlsx (входящий файл)
#               outbox/
#                   korona_zamok_retail_ГГГГММДДЧЧММ.xlsx
#                   korona_zamok_wholesale_ГГГГММДДЧЧММ.xlsx
#                   korona_kurasovschina_retail_ГГГГММДДЧЧММ.xlsx
#                   korona_kurasovschina_wholesale_ГГГГММДДЧЧММ.xlsx
#               inbox_archive/ (упакованные копии вх.файлов)
#                   krynka_ГГГГММДДЧЧММСС.xlsx.gz
#                   krynka_ГГГГММДДЧЧММСС.xlsx.gz
#                   myasokombinat_ГГГГММДДЧЧММСС.xlsx.gz
#                   myasokombinat_ГГГГММДДЧЧММСС.xlsx.gz
#           ...
#           log/
#               pricegen-stat-ГГГГММДД.log (текущий)
#               pricegen-stat-ГГГГММДД.log.gz (за предыдущие даты)
#               pricegen-err-ГГГГММДД.log (текущий)
#               pricegen-err-ГГГГММДД.log.gz (за предыдущие даты)

import time, os, pwd, re, datetime, shutil
import subprocess

from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Min

from pricegen.utils import time_human

from users.models import Org, PickPoint
from pricelists.models import ExcelFormat, ExcelTempo, PickPointDelivery, PickPointBrand, \
    Marge

class Command(BaseCommand):
    help = "generate pricelists after input files detected"

    root_folder = None
    # Дескрипторы журналов
    #
    fd = dict(
        stat=None,
        error=None,
        log=None,
    )

    def add_arguments(self, parser):
        parser.add_argument('root_folder')

    def handle(self, *args, **options):
        root_folder = options['root_folder']
        self.root_folder = root_folder

        # Нельзя запускать, если другой аналогичные процесс крутится
        #
        ps = subprocess.check_output(('ps', '-ef',)).decode('utf-8').split('\n')
        userid = pwd.getpwuid(os.getuid()).pw_name
        pid = os.getpid()
        for p in ps:
            # пропускаем процессы с другим именем
            #
            if not re.search(r'manage\.py\s+generate_pricelists\s+%s' % re.escape(root_folder), p):
                continue
            # пропускаем наш процесс: с нашим именем пользователя и pid процесса
            #
            if re.search(r'^%s\s+%s\s+' % (userid, pid,), p):
                continue
            print('Another same process running. Do not want problems. Quit.')
            quit()

        # Создать каталог для журналов, если он не существует
        #
        quarantine_folder = os.path.join(root_folder, settings.FS_QUARANTINE_FOLDER)
        log_folder = os.path.join(root_folder, settings.FS_LOG_FOLDER)
        for folder in (quarantine_folder, log_folder,):
            if not os.path.isdir(folder):
                try:
                    os.mkdir(folder)
                except OSError:
                    print('ERROR: Failed to create %s folder' % folder)
                    quit()

        # Глобальный цикл. Выходим из него, когда не найдем файлов для обработки
        #
        while True:
            found_input = False

            # Цикл (1). Читаем по всем организациям, все они могут быть продавцами
            #
            for vendor in Org.objects.all():
                
                # Если у продавца нет pickpoints или не найден supplier
                # по имени папки suppliers/<supplier>, то входные 
                #
                ignore_vendor_input = False
                vendor_folder = os.path.join(root_folder, vendor.short_name)
                
                # Цикл (2) . По каталогам, имена которых организации-поставщики
                #
                try:
                    vendors_suppliers_folder = os.path.join(vendor_folder, 'suppliers')
                    suppliers_folders = os.listdir(vendors_suppliers_folder)
                except FileNotFoundError:
                    # Например, нет каталога ...pricegen/krynka/suppliers.
                    # Если krynka - только поставщик, но никак не покупатель, то ОК
                    #
                    continue
                # Есть ли продавца pickpoints. Заодно запомним pickpoints
                #
                pickpoint_deliveries_to = PickPointDelivery.objects.filter(pickpoint_to__org=vendor). \
                    select_related('pickpoint_from')
                if not pickpoint_deliveries_to:
                    self.write_log("No pickpoint deliveries at vendor organization: %s. Move all vendor's input, if any, to quarantine" % (
                            vendor.short_name
                        ), 'error')
                    ignore_vendor_input = True
                for supplier_folder in suppliers_folders:
                    ignore_supplier_input = False
                    path_to_supplier_folder = os.path.join(vendors_suppliers_folder, supplier_folder)
                    if not os.path.isdir(path_to_supplier_folder):
                        continue
                    try:
                        Org.objects.get(short_name=supplier_folder)
                    except Org.DoesNotExist:
                        ignore_supplier_input = True
                        self.write_log("%s, no appropriate organization: %s.  Move all input to the supplier, if any, to quarantine" % (
                                path_to_supplier_folder,
                                supplier_folder
                            ), 'error')
                    xlsx_files = []
                    for xlsx_file in os.listdir(path_to_supplier_folder):
                        path_to_xlsx_file = os.path.join(path_to_supplier_folder, xlsx_file)
                        if not os.path.isfile(path_to_xlsx_file) or \
                               os.path.islink(path_to_xlsx_file) or \
                           not re.search(r'\.xlsx$', xlsx_file, flags=re.I):
                            continue
                        if ignore_vendor_input or ignore_supplier_input:
                            self.put_to_quarantine(path_to_xlsx_file)
                            continue
                        stat = os.stat(path_to_xlsx_file)
                        xlsx_files.append(dict(
                            name=xlsx_file,
                            mtime=stat.st_mtime
                        ))
                        self.write_log('Found input xlsx "%s", supplier %s to vendor %s' % (
                                xlsx_file,
                                supplier_folder,
                                vendor.short_name,
                            ),'log')
                    if ignore_vendor_input or ignore_supplier_input:
                        continue
                    xlsx_files = sorted(xlsx_files, key=lambda d: d['mtime'])
                    xlsx_files = [d['name'] for d in xlsx_files]
                    for xlsx_file in xlsx_files:
                        found_input = True
                        path_to_xlsx_file = os.path.join(path_to_supplier_folder, xlsx_file)
                        if not self.load_xlsx_to_tempo(path_to_xlsx_file, vendor):
                            self.write_log('Error reading ExcelX file: %s' % (
                                    path_to_xlsx_file,
                                ), 'error')
                            self.put_to_quarantine(path_to_xlsx_file)
                            continue
                        pickpoints_to = list()
                        for pickpoint_delivery_to in pickpoint_deliveries_to:
                            pickpoint_to = pickpoint_delivery_to.pickpoint_to
                            # Запоминаем marge
                            #
                            marges = self.get_marges(pickpoint_to)
                            print(marges)
                            for pickpoint_to_brand in PickPointBrand.objects.filter(pickpoint=pickpoint_to):
                                # Здесь вычислить минимальное время доставки этого brand
                                # к этому pickpoint_to, mvd
                                #
                                mvd = PickPointDelivery.objects.filter(
                                    pickpoint_to__org=vendor,
                                    pickpoint_from__pickpointbrand__brand=pickpoint_to_brand.brand,
                                ).aggregate(Min('delivery_time'))
                                mvd = mvd['delivery_time__min']
                                if mvd is None:
                                    # Нет среди складов поставщиков такого, чтоб там был
                                    # этот brand
                                    continue
                                mvd_human = time_human(mvd)
                                pickpoint_to_brand_name = pickpoint_to_brand.brand.name
                                print (pickpoint_to_brand_name, mvd_human)
                                for xlsx_rec in ExcelTempo.objects.filter(
                                   brand__iexact=pickpoint_to_brand_name,
                                   ).order_by('row'):
                                    pass
                        found_input = False
                        # os.unlink(path_to_xlsx_file)

            if not found_input:
                break

    def get_marges(self, pickpoint_to):
        """
        Получить маржи по пункту продажи, сортированные по limit
        """
        marges = list()
        for marge in Marge.objects.filter(pickpoint=pickpoint_to). \
            order_by('pickpoint', 'limit'):
            marges.append(dict(
                limit=marge.limit,
                marge=marge.marge,
            ))
        return marges

    def put_to_quarantine(self, path_to_xlsx_file):
        utc_time = int(time.time())
        dt = datetime.datetime.fromtimestamp(utc_time)
        dt_folder = dt.strftime('%Y-%m-%d~%H-%M-%S')
        dt_folder = os.path.join(self.root_folder, settings.FS_QUARANTINE_FOLDER, dt_folder)
        os.mkdir(dt_folder)
        shutil.move(path_to_xlsx_file, dt_folder)
        self.write_log('%s moved to %s' % (
                path_to_xlsx_file,
                dt_folder,
            ), 'error')

    def load_xlsx_to_tempo(self, path_to_xlsx_file, vendor):
        """
        Загрузить Excel файл во временную таблицу
        
        Параметры:
            path_to_xlsx_file
            vendor: организация, у нее ищем формат Excel файла
        """
        input_col_numbers = self.xlsx_col_numbers(vendor, input_=True)
        try:
            wb = load_workbook(filename=path_to_xlsx_file)
        except:
            return False
        sheet = wb.active
        ExcelTempo.objects.all().delete()
        rows = sheet.rows
        nrow = 0
        for row in rows:
            nrow += 1
            rec = ExcelTempo()
            rec.row = nrow
            for field in input_col_numbers:
                # a_field_col -> a_field
                db_field = field[:-4]
                # print (field, input_col_numbers[field], row[input_col_numbers[field]])
                setattr(rec, db_field, row[input_col_numbers[field]].value)
            rec.save()
        return True

    def xlsx_col_numbers(self, org, input_):
        """
        Получить номера колонок в Excel файле
        
        Параметр:
            vendor:     организация, у нее ищем формат Excel файла
            input_:     True для входного файла, False для выходного
        """
        try:
            xf = ExcelFormat.objects.get(org=org)
            input_col_numbers = dict(
                inner_id_col=xf.inner_id_col,
                partnumber_col=xf.partnumber_col,
                brand_col=xf.brand_col,
                item_name_col=xf.item_name_col,
                price_col=xf.price_col,
                quantity_col=xf.quantity_col,
                delivery_time_col=xf.delivery_time_col,
            )
        except ExcelFormat.DoesNotExist:
            input_col_numbers = settings.XLSX_COL_NUMBERS_DEFAULT.copy()
        if input_:
            for k in settings.XLSX_OUTPUT_ONLY_COLS:
                del input_col_numbers[k]
        for item in input_col_numbers:
            input_col_numbers[item] -=1
        return input_col_numbers

    def write_log(self, rec, kind='stat'):
        """
        Запись в журнал, статистики или ошибок: kind = stat или error или log
        
        Журналы ведутся по принципу, например, для статистики:
        pricegen-stat-ГГГГММДД.log (текущий)
        pricegen-stat-ГГГГММДД.log.gz (за предыдущие даты)
        """
        if kind == 'stat':
            log_name_prefix = settings.FS_STAT_PREFIX
        elif kind == 'log':
            log_name_prefix = settings.FS_LOG_PREFIX
        elif kind == 'error':
            log_name_prefix = settings.FS_ERROR_PREFIX
        else:
            return
        utc_time = int(time.time())
        dt = datetime.datetime.fromtimestamp(utc_time)
        yyyymmdd = '%d%02d%02d' % (dt.year, dt.month, dt.day)
        log_name = '%s%s.%s' % (log_name_prefix, yyyymmdd, settings.FS_LOG_EXT)
        log_folder = os.path.join(self.root_folder, settings.FS_LOG_FOLDER)
        log_name = os.path.join(log_folder, log_name)
        if not os.path.isfile(log_name):
            # Заархивировать все предыдущие журналы
            #
            for f in self.fd:
                if self.fd[f]:
                    self.fd[f].close()
                    self.fd[f] = None
            for f in os.listdir(log_folder):
                fname = os.path.join(log_folder, f)
                if os.path.isfile(fname) and \
                   re.search(r'^%s\d{8}\.%s$' % (
                       re.escape(log_name_prefix),
                       re.escape(settings.FS_LOG_EXT),
                   ), f):
                    os.system('%s %s' % (settings.CMD_ZIP, fname))
        if not self.fd[kind]:
            self.fd[kind] = open(log_name, 'a')
        if kind == 'stat':
            dt_prefix = '%s\t' % utc_time
        else:
            dt_prefix = dt.strftime('%Y-%m-%d %H:%M:%S ')
        self.fd[kind].write('%s%s\n' % (dt_prefix, rec,))
