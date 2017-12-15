from django.contrib import admin

from pricegen.models import BaseModelAdmin
from .models import Org, PickPoint

admin.site.register(Org, BaseModelAdmin)
admin.site.register(PickPoint, BaseModelAdmin)
