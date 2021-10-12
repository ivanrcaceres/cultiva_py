# Generated by Django 2.2.21 on 2021-09-24 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20210923_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helprequest',
            name='message',
            field=models.CharField(db_index=True, help_text='Here you can tell in detail what you need, <b> the better you tell your situation the more likely they want to help you </b>', max_length=200, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Detalle'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='message',
            field=models.CharField(db_index=True, help_text='Here you can tell in detail what you need, <b> the better you tell your situation the more likely they want to help you </b>', max_length=200, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='historicalhelprequest',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Detalle'),
        ),
    ]
