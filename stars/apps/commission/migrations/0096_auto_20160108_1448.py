# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0095_productorder_pay_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productorder',
            name='pay_type',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, '\u4f59\u989d'), (2, '\u7b2c\u4e09\u65b9')]),
        ),
    ]
