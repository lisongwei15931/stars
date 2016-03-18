# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0016_product_trader'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_associate',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u5173\u8054'),
        ),
    ]
