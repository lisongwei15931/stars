# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0013_auto_20151023_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_open', models.BooleanField(default=False, verbose_name='\u662f\u5426\u9ed8\u8ba4')),
                ('bank_start_time', models.TimeField(verbose_name='\u94f6\u884c\u5f00\u59cb\u65f6\u95f4')),
                ('bank_end_time', models.TimeField(verbose_name='\u94f6\u884c\u5173\u95ed\u65f6\u95f4')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u7cfb\u7edf\u914d\u7f6e\u8868',
                'verbose_name_plural': '\u7cfb\u7edf\u914d\u7f6e\u8868',
            },
        ),
    ]
