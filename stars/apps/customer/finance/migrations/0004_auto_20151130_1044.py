# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20151128_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abrescindcontractlog',
            name='summary',
            field=models.CharField(default=b'', max_length=1000, blank=True),
        ),
        migrations.AlterField(
            model_name='absignincontractlog',
            name='summary',
            field=models.CharField(default=b'', max_length=1000, blank=True),
        ),
        migrations.AlterField(
            model_name='absignincontractlog',
            name='sys_comment',
            field=models.CharField(default=b'', max_length=2000, blank=True),
        ),
    ]
