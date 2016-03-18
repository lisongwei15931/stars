# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20151123_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='cert_type',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='\u8bc1\u4ef6\u7c7b\u578b', blank=True, choices=[(0, '\u8eab\u4efd\u8bc1'), (1, '\u7ec4\u7ec7\u673a\u6784\u4ee3\u7801')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(default=b'member', max_length=100, verbose_name='\u89d2\u8272', choices=[(b'member', '\u4f1a\u5458'), (b'ISP', '\u5382\u5546'), (b'dashboard_admin', '\u540e\u53f0\u7ba1\u7406\u5458'), (b'warehouse_staff', '\u4ed3\u5e93\u4eba\u5458'), (b'member_unit', '\u4f1a\u5458\u5355\u4f4d'), (b'trader', '\u4ea4\u6613\u5458')]),
        ),
    ]
