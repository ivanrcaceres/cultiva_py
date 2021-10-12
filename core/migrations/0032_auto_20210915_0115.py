# Generated by Django 2.2.21 on 2021-09-15 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20210914_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helprequest',
            name='title',
            field=models.CharField(db_index=True, help_text='Producto que queres vender', max_length=200, verbose_name='Producto'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='unidad_medida',
            field=models.CharField(blank=True, choices=[('a', 'KILOGRAMOS'), ('b', 'LITROS'), ('c', 'UNIDAD'), ('d', 'DOCENA')], max_length=2, null=True, verbose_name='UNIDAD DE MEDIDA'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='title',
            field=models.CharField(db_index=True, help_text='Producto que queres vender', max_length=200, verbose_name='Producto'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='unidad_medida',
            field=models.CharField(blank=True, choices=[('a', 'KILOGRAMOS'), ('b', 'LITROS'), ('c', 'UNIDAD'), ('d', 'DOCENA')], max_length=2, null=True, verbose_name='UNIDAD DE MEDIDA'),
        ),
    ]
