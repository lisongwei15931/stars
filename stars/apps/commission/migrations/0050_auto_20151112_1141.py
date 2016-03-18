# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0049_auto_20151111_1920'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stockticker',
            unique_together=set([('product', 'created_date')]),
        ),
    ]
