# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20151202_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abrechargewithdrawlog',
            name='inst_serial',
            field=models.CharField(default=b'', unique=True, max_length=60, blank=True),
        ),
        migrations.AlterField(
            model_name='abrescindcontractlog',
            name='inst_serial',
            field=models.CharField(default=b'', unique=True, max_length=60, blank=True),
        ),
        migrations.AlterField(
            model_name='absignincontractlog',
            name='inst_serial',
            field=models.CharField(default=b'', unique=True, max_length=60, blank=True),
        ),
    ]
