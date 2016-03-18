# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0004_auto_20151111_1645'),
        ('commission', '0080_auto_20151221_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='addr',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u8ba2\u5355\u5730\u5740', blank=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='city',
            field=models.ForeignKey(related_name='order_city', verbose_name='\u57ce\u5e02', blank=True, to='address.City', null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='pickup_list',
            field=models.ForeignKey(related_name='order_pickup_list', verbose_name='\u63d0\u8d27\u5355', blank=True, to='commission.PickupList', null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='pickup_type',
            field=models.SmallIntegerField(default=1, choices=[(1, b'\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe7\x89\xa9\xe6\xb5\x81')]),
        ),
        migrations.AddField(
            model_name='productorder',
            name='province',
            field=models.ForeignKey(related_name='order_province', verbose_name='\u7701', blank=True, to='address.Province', null=True),
        ),
        migrations.AddField(
            model_name='tradecomplete',
            name='order',
            field=models.ForeignKey(related_name='trade_order', verbose_name='\u8ba2\u5355', blank=True, to='commission.ProductOrder', null=True),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '\u672a\u652f\u4ed8'), (1, '\u652f\u4ed8\u4e2d'), (2, '\u652f\u4ed8\u6210\u529f'), (3, '\u652f\u4ed8\u5931\u8d25'), (4, '\u5df2\u5173\u95ed'), (5, '\u5df2\u64a4\u9500'), (6, '\u672a\u53d1\u8d27'), (7, '\u5df2\u53d1\u8d27'), (8, '\u90e8\u5206\u63d0\u8d27'), (9, '\u5df2\u63d0\u8d27')]),
        ),
    ]
