# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 22:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myclient', '0005_auto_20170504_0103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='naznach_two',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myclient.Naznach', verbose_name='Назначение №2'),
        ),
    ]
