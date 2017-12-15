# Generated by Django 2.0 on 2017-12-15 17:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricelists', '0003_auto_20171215_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marge',
            name='marge',
            field=models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
