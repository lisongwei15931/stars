# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0004_auto_20151111_1645'),
        ('commission', '0058_auto_20151120_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpickupcity',
            name='city_name',
        ),
        migrations.RemoveField(
            model_name='userpickupcity',
            name='city',
        ),
        migrations.AddField(
            model_name='userpickupcity',
            name='city',
            field=models.ManyToManyField(related_name='pickup_city', verbose_name='\u57ce\u5e02', to='address.City', blank=True),
        ),
    ]
