# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0022_userproduct_total'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pickuplist',
            options={'verbose_name': '\u63d0\u8d27\u5355\u8868', 'verbose_name_plural': '\u63d0\u8d27\u5355\u8868'},
        ),
        migrations.RenameField(
            model_name='pickuplist',
            old_name='user_address_id',
            new_name='user_address',
        ),
        migrations.RenameField(
            model_name='pickuplist',
            old_name='user_picked_id',
            new_name='user_picked_addr',
        ),
    ]
