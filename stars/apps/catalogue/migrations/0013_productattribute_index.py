# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20151107_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattribute',
            name='index',
            field=models.IntegerField(null=True, verbose_name='\u6392\u5e8f', blank=True),
        ),
    ]
