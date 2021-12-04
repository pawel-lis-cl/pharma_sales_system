# Generated by Django 3.2.9 on 2021-12-04 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=128, verbose_name='Nazwa firmy: ')),
                ('nip', models.IntegerField(verbose_name='NIP: ')),
                ('regon', models.IntegerField(verbose_name='REGON: ')),
                ('krs', models.IntegerField(null=True, verbose_name='Numer KRS = ')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=32, verbose_name='Numer Faktury: ')),
                ('date', models.DateField(auto_now=True, verbose_name='Data wystawienia: ')),
                ('status', models.IntegerField(choices=[(1, 'Opłacona'), (2, 'Nieopłacona'), (3, 'Po terminie')], verbose_name='Status płatności: ')),
                ('payment_date', models.DateField(verbose_name='Termin płatności: ')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Nazwa produktu')),
                ('description', models.TextField(null=True, verbose_name='Opis: ')),
                ('active_substance', models.CharField(max_length=64, verbose_name='Substancja czynna')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dose', models.IntegerField(verbose_name='Dawka: ')),
                ('unit', models.IntegerField(choices=[(1, 'mg'), (2, 'ml')], verbose_name='Jednostka(dawki): ')),
                ('in_package', models.IntegerField(verbose_name='Ilość w Opakowaniu')),
                ('photo_10', models.ImageField(null=True, upload_to='img/products/', verbose_name='Zdjęcie 10: ')),
                ('next_delivery', models.DateField(null=True, verbose_name='Planowana data następnej dostawy: ')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager_app.product', verbose_name='Produkt: ')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=32, verbose_name='Numer zamówienia: ')),
                ('order_quantity', models.IntegerField(verbose_name='Ilość: ')),
                ('discount', models.IntegerField(verbose_name='Zniżka: ')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='manager_app.client', verbose_name='Klient: ')),
                ('invoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager_app.invoice', verbose_name='Faktura: ')),
                ('variant', models.ManyToManyField(related_name='order', to='manager_app.Variant', verbose_name='Pozycje: ')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64, verbose_name='Imię: ')),
                ('last_name', models.CharField(max_length=64, verbose_name='Nazwisko: ')),
                ('phone', models.IntegerField(verbose_name='Numer telefonu: ')),
                ('email', models.CharField(max_length=80, verbose_name='Eadres e-mail: ')),
                ('role', models.CharField(max_length=128, verbose_name='Stanowisko: ')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktywny: ')),
                ('supervisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager_app.employee', verbose_name='Przełożony: ')),
            ],
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=8, verbose_name='numer Partii: ')),
                ('ean', models.IntegerField(verbose_name='EAN: ')),
                ('expiration_date', models.DateField(verbose_name='data Przydatności do użycia: ')),
                ('netto', models.FloatField(verbose_name='cena netto: ')),
                ('vat', models.IntegerField(choices=[(1, '0.08'), (2, '0.23')], verbose_name='Starka podatku vat: ')),
                ('quantity', models.IntegerField(verbose_name='Ilość produktów: ')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager_app.variant', verbose_name='Produkt: ')),
            ],
        ),
        migrations.CreateModel(
            name='Adress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=20, verbose_name='Miejscowość; ')),
                ('street', models.CharField(max_length=64, verbose_name='Ulica: ')),
                ('building_number', models.CharField(max_length=8, verbose_name='Numer budynku: ')),
                ('apartment_number', models.CharField(max_length=8, null=True, verbose_name='Numer lokalu: ')),
                ('zip_code', models.CharField(max_length=6, verbose_name='Kod pocztowy')),
                ('type', models.IntegerField(choices=[(1, 'Adres korespondencyjny'), (2, 'Adres Rejestracyjny')], verbose_name='rodzaj adresu')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager_app.client', verbose_name='Klient: ')),
            ],
        ),
    ]
