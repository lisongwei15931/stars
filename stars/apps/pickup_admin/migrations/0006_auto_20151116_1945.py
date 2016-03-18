# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_admin', '0005_pickupstatistics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickupstatistics',
            name='pickup_type',
            field=models.IntegerField(default=b'1', verbose_name='\u63d0\u8d27\u7c7b\u578b', choices=[(b'1', b'\xe8\x87\xaa\xe6\x8f\x90'), (b'2', b'\xe8\x87\xaa\xe6\x8f\x90\xe7\x82\xb9\xe4\xbb\xa3\xe8\xbf\x90')]),
        ),
        migrations.AlterField(
            model_name='pickupstatistics',
            name='quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6570\u91cf', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='pickupstatistics',
            unique_together=set([('pickup_addr', 'product', 'pickup_type')]),
        ),
    ]
