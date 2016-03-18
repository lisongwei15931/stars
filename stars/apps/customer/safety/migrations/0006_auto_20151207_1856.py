# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0005_auto_20151123_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsverificationcode',
            name='type',
            field=models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, '\u4fee\u6539\u624b\u673a\u53f7\u7801-\u9a8c\u8bc1\u65e7\u624b\u673a'), (2, '\u4fee\u6539\u624b\u673a\u53f7\u7801-\u9a8c\u8bc1\u65b0\u624b\u673a'), (3, '\u4fee\u6539\u8d44\u91d1\u5bc6\u7801'), (4, '\u4fee\u6539\u90ae\u7bb1'), (5, '\u4fee\u6539\u767b\u5f55\u5bc6\u7801'), (6, '\u9a8c\u8bc1\u624b\u673a'), (7, '\u89e3\u7ed1\u94f6\u884c\u5361')]),
        ),
    ]
