# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ad', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rollingad',
            name='link_url',
            field=models.URLField(max_length=128, verbose_name='\u94fe\u63a5\u5730\u5740'),
        ),
    ]
