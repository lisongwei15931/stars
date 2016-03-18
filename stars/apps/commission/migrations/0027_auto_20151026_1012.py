# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0026_pickuplist_pickup_captcha'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userassetdailyreport',
            old_name='market_catitalization',
            new_name='market_capitalization',
        ),
    ]
