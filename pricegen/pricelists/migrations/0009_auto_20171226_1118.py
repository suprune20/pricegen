# Generated by Django 2.0 on 2017-12-26 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricelists', '0008_auto_20171221_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exceltempo',
            name='delivery_time',
        ),
        migrations.AddField(
            model_name='exceltempo',
            name='row',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='exceltempo',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=15),
        ),
    ]