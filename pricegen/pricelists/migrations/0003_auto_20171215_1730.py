# Generated by Django 2.0 on 2017-12-15 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('pricelists', '0002_auto_20171215_1257'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='marge',
            unique_together={('pickpoint', 'kind', 'limit')},
        ),
    ]