# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_auto_20151130_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='broker',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='enable_bala',
            field=models.CharField(default=b'', max_length=30),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='host_serial',
            field=models.CharField(default=b'', max_length=60, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='inst_ratifier',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='money_usage',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='money_usage_info',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='summary',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='taster',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='abrescindcontractlog',
            name='status',
            field=models.SmallIntegerField(choices=[(1, '\u6210\u529f'), (2, '\u5931\u8d25'), (3, '\u672a\u63d0\u4ea4'), (4, '\u5904\u7406\u4e2d')]),
        ),
    ]
