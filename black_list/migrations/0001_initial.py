# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-27 23:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Имя')),
                ('tel', models.CharField(max_length=20, verbose_name='Телефон')),
                ('text', models.TextField(verbose_name='Заметка')),
                ('data', models.DateTimeField(auto_now=True, verbose_name='Дата')),
            ],
            options={
                'verbose_name_plural': 'Черные списки',
                'verbose_name': 'Черный список',
                'db_table': 'black_list',
            },
        ),
    ]
