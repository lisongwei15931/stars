# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0028_auto_20151026_1632'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userassetdailyreport',
            unique_together=set([('user', 'target_date')]),
        ),
    ]
