from django.db import models
from django.contrib.auth.models import User

from pricegen.models import BaseModel
from pricegen.utils import ShortNameValidator

class Org(BaseModel):
    ROLE_RETAILER = 'retailer'
    ROLE_SUPPLIER = 'supplier'
    ROLES = (
        (ROLE_SUPPLIER, 'Поставщик'),
        (ROLE_RETAILER, 'Продавец'),
    )

    name = models.CharField('Название', max_length=255, unique=True)
    short_name = models.CharField(
        'Краткое (латинское) название', 
        max_length=50,
        unique=True,
        validators=(ShortNameValidator(),),
    )
    role = models.CharField('Тип', max_length=50, choices=ROLES)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return '%s: %s' % (self.short_name, self.name,)

class PickPoint(BaseModel):
    org = models.ForeignKey(Org, verbose_name='Организация', on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=255, unique=True)
    short_name = models.CharField(
        'Краткое (латинское) название', 
        max_length=50,
        unique=True,
        validators=(ShortNameValidator(),),
    )

    class Meta:
        unique_together = ('org', 'name', )

    def __str__(self):
        return '%s...%s: %s' % (self.org.short_name, self.short_name, self.name,)
