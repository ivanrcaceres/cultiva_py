# Generated by Django 2.2.24 on 2021-09-22 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_reserva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helprequest',
            name='unidad_medida',
            field=models.CharField(blank=True, choices=[('KILOGRAMOS', 'KILOGRAMOS'), ('LITROS', 'LITROS'), ('UNIDAD', 'UNIDAD'), ('DOCENA', 'DOCENA')], max_length=20, null=True, verbose_name='UNIDAD DE MEDIDA'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='unidad_medida',
            field=models.CharField(blank=True, choices=[('KILOGRAMOS', 'KILOGRAMOS'), ('LITROS', 'LITROS'), ('UNIDAD', 'UNIDAD'), ('DOCENA', 'DOCENA')], max_length=20, null=True, verbose_name='UNIDAD DE MEDIDA'),
        ),
    ]
