# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20150924_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search_value', models.CharField(help_text='\u533a\u95f4\u503c\u8bbe\u7f6e\u6210 eg:30\u5ea6-40\u5ea6', max_length=120, null=True, verbose_name='\u641c\u7d22\u503c', blank=True)),
                ('value_range', models.CharField(choices=[(b'>', '\u4ee5\u4e0a'), (b'<', '\u4ee5\u4e0b')], max_length=120, blank=True, help_text='\u4e0d\u662f\u8303\u56f4\u7684\u5c5e\u6027\u503c\u4e3a\u7a7a', null=True, verbose_name='\u9009\u62e9\u8303\u56f4')),
                ('search_order', models.IntegerField(null=True, verbose_name='\u641c\u7d22\u503c\u6392\u5217\u987a\u5e8f', blank=True)),
                ('chose', models.BooleanField(default=True, verbose_name='\u9009\u62e9\u8be5\u641c\u7d22\u503c')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='product_class',
            field=models.ForeignKey(related_name='categories', blank=True, to='catalogue.ProductClass', help_text='\u9009\u62e9\u5206\u7c7b\u7684\u7c7b\u5c5e\u6027\uff0c\u7ed1\u5b9a\u5206\u7c7b\u5546\u54c1\u5c5e\u6027\u503c', null=True, verbose_name='\u5206\u7c7b\u7c7b\u5c5e\u6027'),
        ),
        migrations.AddField(
            model_name='productattribute',
            name='search_filter',
            field=models.BooleanField(default=True, help_text='\u8bbe\u7f6e\u4e0d\u9700\u8981\u641c\u7d22\u7684\u5c5e\u6027\u503c', verbose_name='\u662f\u5426\u641c\u7d22'),
        ),
        migrations.AddField(
            model_name='searchfilter',
            name='attribute',
            field=models.ForeignKey(verbose_name='Attribute', to='catalogue.ProductAttribute'),
        ),
    ]
