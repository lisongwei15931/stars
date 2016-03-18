# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0074_auto_20151205_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupdetail',
            name='logistics_no',
            field=models.CharField(max_length=255, null=True, verbose_name='\u7269\u6d41\u5355\u53f7', blank=True),
        ),
    ]
