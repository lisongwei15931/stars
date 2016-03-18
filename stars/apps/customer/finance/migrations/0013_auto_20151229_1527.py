# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0012_auto_20151229_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='alipaymenttradeorder',
            name='bank_seq_no',
            field=models.CharField(default=b'', max_length=70, blank=True),
        ),
        migrations.AddField(
            model_name='alipaymenttradeorder',
            name='pay_service_type',
            field=models.CharField(default='directPay', max_length=20, choices=[(b'direct_pay', '\u5373\u65f6\u5230\u8d26'), (b'bank_pay', '\u7f51\u94f6\u652f\u4ed8')]),
            preserve_default=False,
        ),
    ]
