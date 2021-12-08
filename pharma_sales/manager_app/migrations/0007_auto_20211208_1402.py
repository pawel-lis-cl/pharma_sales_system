# Generated by Django 3.2.9 on 2021-12-08 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager_app', '0006_auto_20211208_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='number',
            field=models.CharField(max_length=32, verbose_name='numer Partii'),
        ),
        migrations.AlterField(
            model_name='branch',
            name='visit_hour_from',
            field=models.TimeField(default='08:00', null=True, verbose_name='Wizyty od godziny'),
        ),
        migrations.AlterField(
            model_name='branch',
            name='visit_hour_to',
            field=models.TimeField(default='16:00', null=True, verbose_name='Wizyty do godziny'),
        ),
    ]
