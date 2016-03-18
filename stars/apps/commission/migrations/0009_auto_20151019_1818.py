# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0008_auto_20151019_1709'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pickupaddr',
            options={'verbose_name': '\u63d0\u8d27\u70b9\u8868', 'verbose_name_plural': '\u63d0\u8d27\u70b9\u8868'},
        ),
        migrations.AlterModelOptions(
            name='pickupdetail',
            options={'verbose_name': '\u63d0\u8d27\u660e\u7ec6\u8868', 'verbose_name_plural': '\u63d0\u8d27\u660e\u7ec6\u8868'},
        ),
        migrations.AlterModelOptions(
            name='userbalance',
            options={'verbose_name': '\u7528\u6237\u4f59\u989d\u8868', 'verbose_name_plural': '\u7528\u6237\u4f59\u989d\u8868'},
        ),
        migrations.AlterModelOptions(
            name='userbank',
            options={'verbose_name': '\u7528\u6237\u94f6\u884c\u5361\u8868', 'verbose_name_plural': '\u7528\u6237\u94f6\u884c\u5361\u8868'},
        ),
        migrations.AlterModelOptions(
            name='usermoneychange',
            options={'verbose_name': '\u7528\u6237\u8d44\u4ea7\u53d8\u5316\u8868', 'verbose_name_plural': '\u7528\u6237\u8d44\u4ea7\u53d8\u5316\u8868'},
        ),
        migrations.AlterModelOptions(
            name='userpickupaddr',
            options={'verbose_name': '\u7528\u6237\u81ea\u63d0\u70b9\u8868', 'verbose_name_plural': '\u7528\u6237\u81ea\u63d0\u70b9\u8868'},
        ),
    ]
