# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_admin', '0003_auto_20151114_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeincomeapply',
            name='damaged_quantity',
            field=models.IntegerField(null=True, verbose_name='\u7834\u635f\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='storeincomeapply',
            name='lose_quantity',
            field=models.IntegerField(null=True, verbose_name='\u4e22\u5931\u6570\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='status',
            field=models.CharField(default=b'0', max_length=16, verbose_name='\u6279\u590d\u72b6\u6001', choices=[(b'0', '\u5f85\u5165\u5e93'), (b'1', '\u672a\u5ba1\u6838'), (b'2', '\u5df2\u9a73\u56de'), (b'3', '\u4ed3\u5e93\u5df2\u5ba1\u6838'), (b'4', '\u5df2\u5165\u5e93')]),
        ),
    ]
