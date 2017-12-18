# Generated by Django 2.0 on 2017-12-18 12:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricelists', '0004_auto_20171215_1742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='excelformat',
            name='brand_col',
            field=models.PositiveIntegerField(default=3, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
        migrations.AlterField(
            model_name='excelformat',
            name='delivery_time_col',
            field=models.PositiveIntegerField(default=7, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
        migrations.AlterField(
            model_name='excelformat',
            name='inner_id_col',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
        migrations.AlterField(
            model_name='excelformat',
            name='item_name_col',
            field=models.PositiveIntegerField(default=4, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
        migrations.AlterField(
            model_name='excelformat',
            name='partnumber_col',
            field=models.PositiveIntegerField(default=2, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
        migrations.AlterField(
            model_name='excelformat',
            name='price_col',
            field=models.PositiveIntegerField(default=5, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
        migrations.AlterField(
            model_name='excelformat',
            name='quantity_col',
            field=models.PositiveIntegerField(default=6, validators=[django.core.validators.MaxValueValidator(256)]),
        ),
    ]