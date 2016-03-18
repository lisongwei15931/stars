# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20151103_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_long_image',
            field=models.ImageField(upload_to=b'images/products/%Y/%m/', null=True, verbose_name='\u5e7f\u544a\u957f\u56fe', blank=True),
        ),
    ]
