# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20151201_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='abrechargewithdrawlog',
            old_name='comment',
            new_name='user_comment',
        ),
        migrations.RemoveField(
            model_name='abrescindcontractlog',
            name='comment',
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='sys_comment',
            field=models.CharField(default=b'', max_length=2000, blank=True),
        ),
        migrations.AddField(
            model_name='abrescindcontractlog',
            name='sys_comment',
            field=models.CharField(default=b'', max_length=2000, blank=True),
        ),
        migrations.AddField(
            model_name='abrescindcontractlog',
            name='user_comment',
            field=models.CharField(default=b'', max_length=200, blank=True),
        ),
    ]
