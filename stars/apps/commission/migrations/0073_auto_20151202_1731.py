# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0072_auto_20151202_1709'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MatchDeal',
            new_name='ConfirmDeal',
        ),
    ]
