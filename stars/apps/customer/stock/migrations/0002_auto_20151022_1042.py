# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupprovisionalrecord',
            name='available',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u53ef\u7528'),
        ),
        migrations.AlterUniqueTogether(
            name='pickupprovisionalrecord',
            unique_together=set([('user', 'product')]),
        ),
    ]
