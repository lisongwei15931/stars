# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0073_auto_20151202_1731'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commissionbuy',
            name='commission_no',
        ),
        migrations.RemoveField(
            model_name='commissionbuybackup',
            name='commission_no',
        ),
        migrations.RemoveField(
            model_name='commissionsale',
            name='commission_no',
        ),
        migrations.RemoveField(
            model_name='commissionsalebackup',
            name='commission_no',
        ),
        migrations.RemoveField(
            model_name='tradecomplete',
            name='trade_no',
        ),
    ]
