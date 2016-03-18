# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0083_auto_20151223_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradecomplete',
            name='trade_no',
            field=models.CharField(default=datetime.datetime(2015, 12, 23, 6, 26, 14, 813736, tzinfo=utc), unique=True, max_length=255, verbose_name='\u6210\u4ea4\u7f16\u53f7'),
            preserve_default=False,
        ),
    ]
