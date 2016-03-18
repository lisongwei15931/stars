# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0079_orderinfo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productorder',
            options={'verbose_name': '\u8ba2\u5355', 'verbose_name_plural': '\u8ba2\u5355'},
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='user',
        ),
    ]
