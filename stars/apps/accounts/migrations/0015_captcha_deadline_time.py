# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_userprofile_funds_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='captcha',
            name='deadline_time',
            field=models.DateTimeField(null=True, verbose_name='\u8fc7\u671f\u65f6\u95f4', blank=True),
        ),
    ]
