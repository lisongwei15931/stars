# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20151103_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='register_ip',
            field=models.CharField(max_length=64, null=True, verbose_name='\u6ce8\u518cIP', blank=True),
        ),
    ]
