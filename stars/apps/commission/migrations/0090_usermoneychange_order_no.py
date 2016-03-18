# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0089_auto_20160107_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermoneychange',
            name='order_no',
            field=models.CharField(max_length=255, null=True, verbose_name='\u8ba2\u5355\u7f16\u53f7', blank=True),
        ),
    ]
