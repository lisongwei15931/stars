# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0066_dealfeecollect_dealfeedetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbank',
            name='client_name',
            field=models.CharField(default=b'', max_length=100, verbose_name='\u94f6\u884c\u5ba2\u6237\u59d3\u540d'),
        ),
        migrations.AddField(
            model_name='userbank',
            name='is_business_account',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u5bf9\u516c\u8d26\u6237'),
        ),
    ]
