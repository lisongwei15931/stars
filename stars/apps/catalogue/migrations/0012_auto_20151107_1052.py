# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_product_product_long_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u540d\u5b57')),
                ('attr', models.ManyToManyField(related_name='product_group_attr', verbose_name='\u4ea7\u54c1\u7ec4\u5c5e\u6027', to='catalogue.ProductAttribute', blank=True)),
            ],
            options={
                'verbose_name': '\u4ea7\u54c1\u7ec4',
                'verbose_name_plural': '\u4ea7\u54c1\u7ec4',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_group',
            field=models.ForeignKey(related_name='product_group', verbose_name='\u4ea7\u54c1\u7ec4', blank=True, to='catalogue.ProductGroup', null=True),
        ),
    ]
