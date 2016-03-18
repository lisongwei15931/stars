# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0046_storeincomeapply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeincomeapply',
            name='category',
            field=models.ForeignKey(related_name='category_store', verbose_name='\u5546\u54c1\u5927\u7c7b', blank=True, to='catalogue.Category', null=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='deal_user_id',
            field=models.ForeignKey(related_name='user_deal', verbose_name='\u6279\u590d\u4eba', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='plan_income_date',
            field=models.DateField(null=True, verbose_name='\u8ba1\u5212\u5165\u5e93\u65e5\u671f', blank=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='refuse_desc',
            field=models.CharField(max_length=300, null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True),
        ),
    ]
