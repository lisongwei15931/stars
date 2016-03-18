# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wishlists', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='line',
            options={'managed': True, 'verbose_name': '\u6211\u7684\u5173\u6ce8'},
        ),
        migrations.AddField(
            model_name='line',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 9, 5, 46, 38, 595000, tzinfo=utc), verbose_name='\u6536\u85cf\u65f6\u95f4', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together=set([]),
        ),
    ]
