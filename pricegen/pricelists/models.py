from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from pricegen.models import BaseModel

class ExcelFormat(BaseModel):

    org = models.OneToOneField('users.Org', verbose_name='Организация',
                            on_delete=models.CASCADE)
    inner_id_col = models.PositiveIntegerField(default=1,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))
    partnumber_col = models.PositiveIntegerField(default=2,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))
    brand_col = models.PositiveIntegerField(default=3,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))
    item_name_col = models.PositiveIntegerField(default=4,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))
    price_col = models.PositiveIntegerField(default=5,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))
    quantity_col = models.PositiveIntegerField(default=6,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))
    delivery_time_col = models.PositiveIntegerField(default=7,
                                               validators=(MaxValueValidator(settings.XLSX_MAX_COLS),))

    def __str__(self):
        return 'excelformat: %s (%s)' % (self.org.short_name, self.org.name,)

class Marge(BaseModel):

    KIND_RETAIL = 'retail'
    KIND_WHOLESALE = 'wholesail'
    KINDS = (
        (KIND_RETAIL, 'Розница'),
        (KIND_WHOLESALE, 'Опт'),
    )

    pickpoint = models.ForeignKey('users.PickPoint',
                            on_delete=models.CASCADE)
    kind = models.CharField('Тип', max_length=50, choices=KINDS)
    limit = models.DecimalField(max_digits=15, decimal_places=2,
                                validators=(MinValueValidator(0),))
    marge = models.DecimalField(max_digits=6, decimal_places=2,
                                validators=(MinValueValidator(0),))
    class Meta:
        unique_together = ('pickpoint', 'kind', 'limit')

    def __str__(self):
        return 'marge: %s %s' % (self.pickpoint.short_name, self.kind)

class Brand(BaseModel):

    name = models.CharField('Название', max_length=255, unique=True)

    def __str__(self):
        return self.name

class PickPointBrand(BaseModel):

    pickpoint = models.ForeignKey('users.PickPoint',
                            on_delete=models.CASCADE)
    brand = models.ForeignKey('pricelists.Brand',
                            on_delete=models.CASCADE)

    def __str__(self):
        return '%s...%s: %s' % (self.pickpoint.org.short_name, self.pickpoint.short_name, self.brand.name,)

    class Meta:
        unique_together = ('pickpoint', 'brand', )

class PickPointDelivery(BaseModel):

    pickpoint_from = models.ForeignKey('users.PickPoint', related_name='+',
                            on_delete=models.CASCADE)
    pickpoint_to = models.ForeignKey('users.PickPoint', related_name='+',
                            on_delete=models.CASCADE)
    delivery_time = models.PositiveIntegerField('Время доставки (мин.)')

    class Meta:
        unique_together = ('pickpoint_from', 'pickpoint_to', )

    def __str__(self):
        return '%s...%s - %s...%s' % (
            self.pickpoint_from.org.short_name, self.pickpoint_from.short_name,
            self.pickpoint_to.org.short_name, self.pickpoint_to.short_name,
        )

class ExcelTempo(models.Model):
    """
    ВрЕменная таблица для считываемых из Excel файлов данных
    """
    inner_id = models.CharField(max_length=255)
    partnumber = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, db_index=True)
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2, db_index=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    delivery_time = models.PositiveIntegerField(default=0)

    def delivery_time_human(self):
        """
        Время из минут в '?? час. ?? мин.'
        """
        mins = self.delivery_time
        if not mins:
            return ''
        mins_ = mins % 60
        hours_ = int(mins / 60)
        result = ''
        if hours_:
            result += '%s час.' % hours_
        if mins_ and hours_:
            result += ' '
        if mins_:
            result += '%s мин.' % mins_
        return result
