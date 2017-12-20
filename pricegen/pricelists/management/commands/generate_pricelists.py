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
# pricegen/                                                         (1)
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

        # Цикл (1). Читаем по всем организациям, все они могут быть продавцами
        #
        for vendor in Org.objects.all():
            vendor_folder = os.path.join(root_folder, vendor.short_name, 'suppliers')
            print (vendor_folder)
            
            # Цикл (2) . По каталогам, имена которых организации-поставщики
            #
            try:
                suppliers_folders = os.listdir(vendor_folder)
            except FileNotFoundError:
                # Например, нет каталога pricegen/korona/suppliers
                #
                continue
            
            self.write_log('что-то')
            self.write_log('что-то', 'log')
            #input_files = list()
            #for f in os.listdir(vendor_folder)
                #input_xlsx = os.join(vendor_folder, f)
                #if isfile(input_xlsx) and not islink(input_xlsx):

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
