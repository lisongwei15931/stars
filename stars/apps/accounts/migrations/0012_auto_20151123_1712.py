# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_userprofile_register_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='pay_pwd',
            field=models.CharField(max_length=128, null=True, verbose_name='\u8d44\u91d1\u5bc6\u7801', blank=True),
        ),
    ]
