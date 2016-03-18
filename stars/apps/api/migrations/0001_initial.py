# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=64, verbose_name='\u7248\u672c\u53f7')),
                ('operaing_system', models.CharField(default=b'1', max_length=16, verbose_name='\u64cd\u4f5c\u7cfb\u7edf', choices=[(b'1', b'IOS'), (b'2', b'Android')])),
                ('description', models.TextField(verbose_name='\u7248\u672c\u63cf\u8ff0', blank=True)),
                ('app_file', models.FileField(upload_to=b'apps', verbose_name='APP\u6587\u4ef6')),
                ('need_forced_update', models.BooleanField(default=False, verbose_name='\u662f\u5426\u9700\u8981\u5f3a\u5236\u66f4\u65b0')),
            ],
            options={
                'verbose_name': '\u79fb\u52a8APP',
                'verbose_name_plural': '\u79fb\u52a8APP',
            },
        ),
        migrations.AlterUniqueTogether(
            name='app',
            unique_together=set([('version', 'operaing_system')]),
        ),
    ]
