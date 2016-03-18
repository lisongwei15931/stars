# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0019_auto_20151023_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermoneychange',
            name='parent_id',
            field=models.ForeignKey(related_name='parent_money_chanage', verbose_name='\u7236id', blank=True, to='commission.UserMoneyChange', null=True),
        ),
    ]
