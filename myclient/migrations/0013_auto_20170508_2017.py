# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-08 17:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myclient', '0012_spor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spor',
            name='user_one',
        ),
        migrations.DeleteModel(
            name='Spor',
        ),
    ]