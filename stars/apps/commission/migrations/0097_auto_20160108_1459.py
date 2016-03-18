# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0096_auto_20160108_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productorder',
            name='description',
            field=models.CharField(default=b'', max_length=200, verbose_name='\u5546\u54c1\u63cf\u8ff0', blank=True),
        ),
    ]
