# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0090_usermoneychange_order_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='express_fee',
            field=models.DecimalField(default=0, verbose_name='\u5feb\u9012\u8d39', max_digits=15, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productorder',
            name='pickup_fee',
            field=models.DecimalField(default=0, verbose_name='\u6742\u8d39', max_digits=15, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productorder',
            name='product_price',
            field=models.DecimalField(default=0, verbose_name='\u4ea7\u54c1\u8d39\u7528', max_digits=15, decimal_places=2),
            preserve_default=False,
        ),
    ]
