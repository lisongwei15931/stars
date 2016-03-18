# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staticpages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flatpagenew',
            name='category',
            field=models.IntegerField(default=1, db_index=True, verbose_name='\u7c7b\u522b', choices=[(1, '\u9759\u6001\u9875\u9762'), (2, '\u516c\u544a'), (3, '\u65b0\u54c1\u4e0a\u5e02'), (4, '\u8d2d\u7269\u987b\u77e5'), (5, '\u5176\u4ed6')]),
        ),
    ]
