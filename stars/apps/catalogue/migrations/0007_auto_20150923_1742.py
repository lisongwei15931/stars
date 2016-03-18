# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20150917_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='browse_num',
            field=models.BigIntegerField(default=0, verbose_name='\u6d4f\u89c8\u6b21\u6570'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_on_shelves',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u4e0a\u67b6'),
        ),
    ]
