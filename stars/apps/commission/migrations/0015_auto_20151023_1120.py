# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0014_systemconfig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemconfig',
            name='is_open',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u5f00\u5e02'),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='trade_type',
            field=models.IntegerField(db_index=True, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe5\x85\x85\xe5\x80\xbc'), (2, b'\xe6\x8f\x90\xe7\x8e\xb0'), (3, b'\xe8\xb4\xad\xe4\xb9\xb0\xe5\x86\xbb\xe7\xbb\x93'), (4, b'\xe8\xb4\xad\xe4\xb9\xb0\xe8\xa7\xa3\xe5\x86\xbb'), (5, b'\xe8\xb4\xad\xe4\xb9\xb0\xe6\x88\x90\xe4\xba\xa4'), (6, b'\xe8\xbf\x9b\xe8\xb4\xa7\xe5\x86\xbb\xe7\xbb\x93'), (7, b'\xe8\xbf\x9b\xe8\xb4\xa7\xe8\xa7\xa3\xe5\x86\xbb'), (8, b'\xe8\xbf\x9b\xe8\xb4\xa7\xe6\x88\x90\xe4\xba\xa4'), (9, b'\xe5\x87\xba\xe5\x94\xae'), (10, b'\xe6\x8f\x90\xe8\xb4\xa7\xe5\x86\xbb\xe7\xbb\x93'), (11, b'\xe6\x8f\x90\xe8\xb4\xa7\xe9\xa9\xb3\xe5\x9b\x9e'), (12, b'\xe6\x8f\x90\xe8\xb4\xa7\xe5\xae\x8c\xe6\x88\x90'), (13, b'\xe6\x92\xa4\xe5\x8d\x95')]),
        ),
    ]
