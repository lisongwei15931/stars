# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0032_auto_20151028_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemconfig',
            name='auto_open',
            field=models.BooleanField(default=False, verbose_name='\u81ea\u52a8\u5f00\u5e02'),
        ),
    ]
