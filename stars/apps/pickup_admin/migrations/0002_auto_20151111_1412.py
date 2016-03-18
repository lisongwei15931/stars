# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_admin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeincomeapply',
            name='apply_date',
            field=models.DateField(auto_now_add=True, verbose_name='\u7533\u8bf7\u65e5\u671f', null=True),
        ),
    ]
