# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_receivingaddress'),
        ('accounts', '0007_auto_20151021_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='region',
            field=models.ForeignKey(verbose_name='\u5730\u533a', blank=True, to='address.District', null=True),
        ),
    ]
