# Generated by Django 2.2.21 on 2021-10-09 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_useraux_telefono'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginUserCom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=50, verbose_name='Usuario')),
                ('password', models.CharField(max_length=50, verbose_name='Contraseña')),
            ],
        ),
    ]
