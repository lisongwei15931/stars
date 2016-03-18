# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0094_auto_20160108_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='pay_type',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, '\u8d2d\u4e70'), (2, '\u8fdb\u8d27'), (3, '\u51fa\u552e')]),
        ),
    ]
