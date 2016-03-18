# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlatPageNew',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=200, verbose_name='\u6807\u9898', db_index=True)),
                ('category', models.IntegerField(default=1, db_index=True, verbose_name='\u7c7b\u522b', choices=[(1, '\u9759\u6001\u9875\u9762'), (2, '\u516c\u544a'), (3, '\u65b0\u54c1\u4e0a\u5e02'), (4, '\u5176\u4ed6')])),
                ('url', models.CharField(default=b'', max_length=200, verbose_name='URL')),
                ('content', ckeditor.fields.RichTextField(verbose_name='\u6b63\u6587')),
                ('enable', models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u542f\u7528')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
            ],
        ),
    ]
