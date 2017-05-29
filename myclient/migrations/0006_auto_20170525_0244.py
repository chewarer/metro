# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-24 23:44
from __future__ import unicode_literals

from django.db import migrations, models
import myclient.models


class Migration(migrations.Migration):

    dependencies = [
        ('myclient', '0005_auto_20170523_2350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskclient',
            name='prioritet',
            field=models.ForeignKey(on_delete=models.SET(myclient.models.TaskClient.get_prio), to='myclient.Prioritet', verbose_name='Приоритет'),
        ),
    ]