# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0067_auto_20151201_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupdetail',
            name='trade_type',
            field=models.IntegerField(default=1, verbose_name='\u51fa\u552e\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')]),
        ),
    ]
