# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='audit_status',
            field=models.BooleanField(default=False, verbose_name='\u5ba1\u6838\u72b6\u6001'),
        ),
    ]
