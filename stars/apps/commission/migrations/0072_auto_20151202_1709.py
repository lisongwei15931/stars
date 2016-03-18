# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0071_auto_20151202_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchDeal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commission_buy_id', models.CharField(max_length=255, verbose_name='\u59d4\u6258\u4e70\u7f16\u53f7')),
                ('commission_sale_id', models.CharField(max_length=255, verbose_name='\u59d4\u6258\u5356\u7f16\u53f7')),
            ],
            options={
                'verbose_name': '\u4ea4\u6613\u5339\u914d\u8868',
                'verbose_name_plural': '\u4ea4\u6613\u5339\u914d\u8868',
            },
        ),
        migrations.AlterUniqueTogether(
            name='matchdeal',
            unique_together=set([('commission_buy_id', 'commission_sale_id')]),
        ),
    ]
