from django.db import models
from django.contrib import admin

from django.conf import settings
from django.contrib.auth.models import User

class BaseModel(models.Model):
    """
    Базовый класс для многих моделей. Даты создания/модификации автоматически
    """
    class Meta:
        abstract = True
        
    creator = models.ForeignKey(User, verbose_name='Создатель', on_delete=models.CASCADE,
                                related_name='+', editable=False)
    dt_created = models.DateTimeField('Дата/время создания', auto_now_add=True)
    modifier = models.ForeignKey(User, verbose_name='Изменивший', on_delete=models.CASCADE,
                                 related_name='+', editable=False)
    dt_modified = models.DateTimeField('Дата/время модификации', auto_now=True)

class BaseModelAdmin(admin.ModelAdmin):
    """
    Сохранить создателя и модификатора записей базового класса в админке
    """
    def save_model(self, request, obj, form, change):
        obj.modifier = request.user
        if getattr(obj, 'creator', None) is None:
            obj.creator = request.user
        super().save_model(request, obj, form, change)
