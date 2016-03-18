# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0016_remove_usermoneychange_money_bank_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermoneychange',
            name='money_bank_id',
            field=models.ForeignKey(related_name='money_chanage_bank', default=b'', verbose_name='\u94f6\u884cID', blank=True, to='commission.UserBank'),
        ),
    ]
