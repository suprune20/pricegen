import time, os, pwd, re
import subprocess

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "generate pricelists after input files detected"

    def add_arguments(self, parser):
        parser.add_argument('root_folder')

    def handle(self, *args, **options):
        root_folder = options['root_folder']

        # Нельзя запускать, если другие аналогичные процессы крутятся
        #
        ps = subprocess.check_output(('ps', '-ef',)).decode('utf-8').split('\n')
        userid = pwd.getpwuid(os.getuid()).pw_name
        pid = os.getpid()
        for p in ps:
            # пропускаем процессы с другим именем
            #
            if not re.search(r'manage.py\s+generate_pricelists\s+%s' % re.escape(root_folder), p):
                continue
            # пропускаем наш процесс: с нашим именем пользователя и pid процесса
            #
            if re.search(r'^%s\s+%s\s+' % (userid, pid,), p):
                continue
            print('Another same process running. Do not want problems. Quit.')
            quit()

        time.sleep(30)
