# coding: utf-8

import os, time
from django.conf import settings

def context_processor(request):

    def get_static_updated_time():
        """
        UTC modified timestamp папки settings.STATIC_ROOT

        Во избежание лишнего кэширования в браузере клиента
        статических файлов: javascript- сценариев.

        Все наши сценарии определяются в шаблонах как:

        <script src="{{ STATIC_URL }}js/<сценарий>.js?updated_=<timestamp>">
        </script>

        где <timestamp> - UTC время в секундах изменения папки
        settings.STATIC_ROOT. Это время автоматически обновляется
        процедурой установки нового кода в проекте.
        В этой процедуре, после ./manage.py collectstatic,
        если произошли изменения в папке settings.STATIC_ROOT,
        производится обновление modified timestamp этой
        папки, и этот обновленный <timestamp> приписывается
        в src сценариев. URL сценария меняется, браузер
        должен его перегружать.
        """

        try:
            result = os.stat(settings.STATIC_ROOT).st_mtime
        except (OSError, AttributeError, ):
            # Невероятно, но!
            # Вдруг STATIC_ROOT не определено или ОС доступ
            # закроет к параметрам папки.
            result = time.time()
        return int(result)

    return {
            'global_context_STATIC_UPDATED_TIME': get_static_updated_time(),
           }
