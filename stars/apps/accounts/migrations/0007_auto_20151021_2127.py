# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20151021_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='nickname',
            field=models.CharField(default=b'', max_length=127, null=True, verbose_name='\u6635\u79f0', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='real_name',
            field=models.CharField(default=b'', max_length=127, null=True, verbose_name='\u771f\u5b9e\u59d3\u540d', blank=True),
        ),
    ]
