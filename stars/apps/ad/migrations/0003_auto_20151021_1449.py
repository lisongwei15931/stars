# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ad', '0002_auto_20150928_1437'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rollingad',
            options={'ordering': ['order_num', 'id'], 'verbose_name': 'Rolling advertisement'},
        ),
    ]
