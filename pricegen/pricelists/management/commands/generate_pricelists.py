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

import time, os, pwd, re, datetime
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

from users.models import Org, PickPoint

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
        log_folder = os.path.join(root_folder, settings.FS_LOG_FOLDER)
        if not os.path.isdir(log_folder):
            try:
                os.mkdir(log_folder)
            except OSError:
                print('ERROR: Failed to create %s folder' % log_folder)
                quit()

        # Глобальный цикл. Выходим из него, когда не будет файлов для обработки
        #
        while True:
            found_input = False

            # Цикл (1). Читаем по всем организациям, все они могут быть продавцами
            #
            for vendor in Org.objects.all():
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
                vendor_pickpoints = PickPoint.objects.filter(org=vendor)
                if not vendor_pickpoints:
                    continue
                for supplier_folder in suppliers_folders:
                    path_to_supplier_folder = os.path.join(vendors_suppliers_folder, supplier_folder)
                    if not os.path.isdir(path_to_supplier_folder):
                        continue
                    try:
                        Org.objects.get(short_name=supplier_folder)
                    except Org.DoesNotExist:
                        self.write_log('%s, no appropriate organization: %s' % (
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
                    xlsx_files = sorted(xlsx_files, key=lambda d: d['mtime'])
                    xlsx_files = [d['name'] for d in xlsx_files]
                    for xlsx_file in xlsx_files:
                        pass

            if not found_input:
                break

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
