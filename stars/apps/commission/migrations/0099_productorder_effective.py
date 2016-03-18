# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0098_auto_20160108_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='effective',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u6709\u6548'),
        ),
    ]
