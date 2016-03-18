# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20151208_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='funds_password',
            field=models.CharField(max_length=128, null=True, verbose_name='\u8d44\u91d1\u5bc6\u7801', blank=True),
        ),
    ]
