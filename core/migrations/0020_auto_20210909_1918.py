# Generated by Django 2.2.21 on 2021-09-09 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20210909_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='helprequest',
            name='fecha_disponibilidad',
            field=models.DateField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalhelprequest',
            name='fecha_disponibilidad',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
    ]
