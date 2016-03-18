# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platform', '0002_stockenter_stockid'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockenter',
            name='deal_datetime',
            field=models.DateTimeField(null=True, verbose_name='\u6279\u590d\u65f6\u95f4', blank=True),
        ),
        migrations.AddField(
            model_name='stockenter',
            name='deal_user',
            field=models.ForeignKey(verbose_name='\u6279\u590d\u4eba', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='stockenter',
            name='refuse_desc',
            field=models.CharField(max_length=256, null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True),
        ),
        migrations.AddField(
            model_name='stockenter',
            name='status',
            field=models.CharField(default=b'1', max_length=16, verbose_name='\u72b6\u6001', choices=[(b'1', '\u672a\u5ba1\u6838'), (b'2', '\u5df2\u9a73\u56de'), (b'3', '\u5df2\u901a\u8fc7')]),
        ),
    ]
