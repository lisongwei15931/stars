# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0060_auto_20151121_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbank',
            name='client_no',
            field=models.CharField(default=b'', max_length=100, verbose_name='\u94f6\u884c\u5ba2\u6237\u53f7'),
        ),
        migrations.AddField(
            model_name='userbank',
            name='is_rescinded',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u89e3\u7ea6'),
        ),
    ]
