# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_userprofile_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='introducer',
            field=models.CharField(max_length=64, null=True, verbose_name='\u63a8\u8350\u4eba', blank=True),
        ),
    ]
