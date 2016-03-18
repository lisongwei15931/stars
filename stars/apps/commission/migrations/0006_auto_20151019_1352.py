# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0005_auto_20151019_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickupdetail',
            name='modified_date',
            field=models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='pickupdetail',
            name='modified_time',
            field=models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='modified_date',
            field=models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='modified_time',
            field=models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='modified_date',
            field=models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='modified_time',
            field=models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='modified_date',
            field=models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='modified_time',
            field=models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4'),
        ),
    ]
