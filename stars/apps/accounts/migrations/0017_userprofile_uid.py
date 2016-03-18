# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20151217_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='uid',
            field=models.IntegerField(null=True, verbose_name=b'uid', blank=True),
        ),
    ]
