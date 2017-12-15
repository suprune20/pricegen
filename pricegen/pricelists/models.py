from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from pricegen.models import BaseModel

class ExcelFormat(BaseModel):

    org = models.OneToOneField('users.Org', verbose_name='Организация',
                            on_delete=models.CASCADE)
    inner_id_col = models.PositiveIntegerField(default=1)
    partnumber_col = models.PositiveIntegerField(default=2)
    brand_col = models.PositiveIntegerField(default=3)
    item_name_col = models.PositiveIntegerField(default=4)
    price_col = models.PositiveIntegerField(default=5)
    quantity_col = models.PositiveIntegerField(default=6)
    delivery_time_col = models.PositiveIntegerField(default=7)

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
    marge = models.DecimalField(max_digits=4, decimal_places=2,
                                validators=(MinValueValidator(0),))
    class Meta:
        unique_together = ('pickpoint', 'kind', )

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
