from django.contrib import admin

from pricegen.models import BaseModelAdmin
from .models import ExcelFormat, Marge, Brand, PickPointBrand, PickPointDelivery, ExcelTempo

admin.site.register(ExcelFormat, BaseModelAdmin)

class MargeAdmin(BaseModelAdmin):
    list_display = ('pickpoint', 'kind', 'limit', 'marge')

admin.site.register(Marge, MargeAdmin)

admin.site.register(Brand, BaseModelAdmin)
admin.site.register(PickPointBrand, BaseModelAdmin)
admin.site.register(PickPointDelivery, BaseModelAdmin)
admin.site.register(ExcelTempo)
