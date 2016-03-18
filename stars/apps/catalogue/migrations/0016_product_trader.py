# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0015_auto_20151130_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='trader',
            field=models.ForeignKey(related_name='trader', verbose_name='\u4ea4\u6613\u5458', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
