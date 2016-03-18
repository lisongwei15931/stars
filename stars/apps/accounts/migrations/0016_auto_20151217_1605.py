# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_captcha_deadline_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='sex',
            field=models.PositiveSmallIntegerField(default=3, verbose_name='\u6027\u522b', choices=[(1, '\u7537'), (2, '\u5973'), (3, '\u4fdd\u5bc6')]),
        ),
    ]
