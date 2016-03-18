# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_productattribute_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='opening_date',
            field=models.DateField(default=django.utils.timezone.now, null=True, verbose_name='\u4e0a\u5e02\u65f6\u95f4', blank=True),
        ),
    ]
