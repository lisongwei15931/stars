# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_auto_20151203_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='trade_date',
            field=models.DateField(verbose_name='\u4ea4\u6613\u65e5\u671f', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='trade_time',
            field=models.TimeField(verbose_name='\u4ea4\u6613\u65f6\u95f4', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='abrechargewithdrawlog',
            name='transfer_amount',
            field=models.DecimalField(max_digits=30, decimal_places=5),
        ),
    ]
