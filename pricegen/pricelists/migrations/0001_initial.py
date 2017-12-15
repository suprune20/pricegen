# Generated by Django 2.0 on 2017-12-15 12:36

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата/время создания')),
                ('dt_modified', models.DateTimeField(auto_now=True, verbose_name='Дата/время модификации')),
                ('inner_id_col', models.PositiveIntegerField(default=1)),
                ('partnumber_col', models.PositiveIntegerField(default=2)),
                ('brand_col', models.PositiveIntegerField(default=3)),
                ('item_name_col', models.PositiveIntegerField(default=4)),
                ('price_col', models.PositiveIntegerField(default=5)),
                ('quantity_col', models.PositiveIntegerField(default=6)),
                ('delivery_time_col', models.PositiveIntegerField(default=7)),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
                ('modifier', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменивший')),
                ('org', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.Org', verbose_name='Организация')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Marge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата/время создания')),
                ('dt_modified', models.DateTimeField(auto_now=True, verbose_name='Дата/время модификации')),
                ('kind', models.CharField(choices=[('retail', 'Розница'), ('wholesail', 'Опт')], max_length=50, verbose_name='Тип')),
                ('limit', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('marge', models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(0)])),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
                ('modifier', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменивший')),
                ('pickpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.PickPoint')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='marge',
            unique_together={('pickpoint', 'kind')},
        ),
    ]
