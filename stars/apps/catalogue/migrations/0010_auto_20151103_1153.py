# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20151031_1425'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='searchfilter',
            options={'ordering': ['attribute'], 'verbose_name': '\u641c\u7d22\u5c5e\u6027\u914d\u7f6e', 'verbose_name_plural': '\u641c\u7d22\u5c5e\u6027\u914d\u7f6e'},
        ),
    ]
