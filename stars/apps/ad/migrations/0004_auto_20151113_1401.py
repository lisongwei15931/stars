# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ad', '0003_auto_20151021_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rollingad',
            name='position',
            field=models.CharField(max_length=30, verbose_name='\u5e7f\u544a\u4f4d\u7f6e', choices=[(b'home_ad', b'\xe4\xb8\xbb\xe9\xa1\xb5\xe8\xbd\xae\xe6\x92\xad'), (b'home_ad_1', b'\xe4\xb8\xbb\xe9\xa1\xb5\xe6\x96\xb0\xe5\x93\x81'), (b'home_ad_2', b'\xe4\xb8\xbb\xe9\xa1\xb5\xe5\x8f\xa3\xe7\xa2\x91'), (b'home_ad_3', b'\xe4\xb8\xbb\xe9\xa1\xb5\xe4\xb8\xbb\xe6\x8e\xa8'), (b'home_ad_4', b'\xe4\xb8\xbb\xe9\xa1\xb5\xe7\x81\xab\xe7\x83\xad'), (b'other', b'\xe5\x85\xb6\xe4\xbb\x96')]),
        ),
    ]
