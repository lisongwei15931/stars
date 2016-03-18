# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20151019_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.CharField(default=b'', max_length=200, verbose_name='\u8be6\u7ec6\u5730\u5740'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='interest',
            field=models.CharField(default=b'', max_length=200, verbose_name='\u5174\u8da3'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sex',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='\u6027\u522b', choices=[(1, '\u4fdd\u5bc6'), (2, '\u7537'), (3, '\u5973')]),
        ),
    ]
