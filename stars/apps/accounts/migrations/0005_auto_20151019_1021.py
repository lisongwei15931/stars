# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151017_1620'),
    ]

    operations = [
        migrations.RunSQL([("ALTER TABLE accounts_userprofile modify column audit_status smallint")]),
        migrations.RunSQL([("ALTER TABLE accounts_userprofile alter column audit_status set DEFAULT 0")]),
        migrations.AlterField(
            model_name='userprofile',
            name='audit_status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u8ba4\u8bc1\u72b6\u6001', choices=[(0, '\u672a\u8ba4\u8bc1'), (1, '\u8ba4\u8bc1\u4e2d'), (2, '\u8ba4\u8bc1\u6210\u529f'), (3, '\u8ba4\u8bc1\u5931\u8d25')]),
        ),
    ]
