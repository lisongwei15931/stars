# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_userprofile_introducer'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(default=b'member', max_length=100, verbose_name='\u89d2\u8272', choices=[(b'member', '\u4f1a\u5458'), (b'ISP', '\u5382\u5546'), (b'dashboard_admin', '\u540e\u53f0\u7ba1\u7406\u5458'), (b'warehouse_staff', '\u4ed3\u5e93\u4eba\u5458')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(default=b'', max_length=200, null=True, verbose_name='\u8be6\u7ec6\u5730\u5740', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='interest',
            field=models.CharField(default=b'', max_length=200, null=True, verbose_name='\u5174\u8da3', blank=True),
        ),
    ]
