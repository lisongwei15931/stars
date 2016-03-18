# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20151127_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='absignincontractlog',
            name='address',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='email',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='fax_no',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='mobile',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='postcode',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='absignincontractlog',
            name='tel_no',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
    ]
