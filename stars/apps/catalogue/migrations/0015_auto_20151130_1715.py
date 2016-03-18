# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_product_opening_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='opening_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='\u4e0a\u5e02\u65f6\u95f4'),
        ),
    ]
