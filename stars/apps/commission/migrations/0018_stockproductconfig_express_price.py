# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0017_usermoneychange_money_bank_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockproductconfig',
            name='express_price',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u5feb\u9012\u8d39\u7528', blank=True),
        ),
    ]
