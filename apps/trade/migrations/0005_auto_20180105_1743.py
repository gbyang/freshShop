# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-05 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0004_auto_20180105_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='post_script',
            field=models.TextField(blank=True, default='', null=True, verbose_name='订单留言'),
        ),
    ]
