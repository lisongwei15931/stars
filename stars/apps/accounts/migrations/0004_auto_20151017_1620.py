# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20151017_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='desc',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
    ]
