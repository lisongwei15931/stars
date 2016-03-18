# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0053_auto_20151112_2029'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userproduct',
            unique_together=set([('user', 'product', 'trade_type')]),
        ),
    ]
