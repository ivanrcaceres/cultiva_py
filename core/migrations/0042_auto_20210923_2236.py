# Generated by Django 2.2.21 on 2021-09-24 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20210923_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdatosextras',
            name='apellido',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='userdatosextras',
            name='nombre',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
