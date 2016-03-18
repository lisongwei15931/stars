# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0010_auto_20151020_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuy',
            name='status',
            field=models.IntegerField(db_index=True, verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4'), (4, b'\xe6\x92\xa4\xe5\x8d\x95')]),
        ),
        migrations.AlterField(
            model_name='commissionbuybackup',
            name='status',
            field=models.IntegerField(db_index=True, verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4'), (4, b'\xe6\x92\xa4\xe5\x8d\x95')]),
        ),
        migrations.AlterField(
            model_name='commissionsale',
            name='status',
            field=models.IntegerField(db_index=True, verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4'), (4, b'\xe6\x92\xa4\xe5\x8d\x95')]),
        ),
        migrations.AlterField(
            model_name='commissionsalebackup',
            name='status',
            field=models.IntegerField(db_index=True, verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4'), (4, b'\xe6\x92\xa4\xe5\x8d\x95')]),
        ),
    ]
