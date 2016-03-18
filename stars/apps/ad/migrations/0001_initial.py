# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RollingAd',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='\u6807\u9898')),
                ('link_url', models.CharField(max_length=128, verbose_name='\u94fe\u63a5\u5730\u5740')),
                ('position', models.CharField(max_length=30, verbose_name='\u5e7f\u544a\u4f4d\u7f6e', choices=[(b'home_ad', b'\xe4\xb8\xbb\xe9\xa1\xb5'), (b'other', b'\xe5\x85\xb6\xe4\xbb\x96')])),
                ('image', models.ImageField(upload_to=b'images/products/%Y/%m/', max_length=255, verbose_name='Image')),
                ('description', models.TextField(default=b'', max_length=255, verbose_name='Description')),
                ('order_num', models.PositiveIntegerField(default=0, verbose_name='\u987a\u5e8f\u53f7')),
                ('valid', models.BooleanField(default=True, verbose_name='\u542f\u7528')),
            ],
            options={
                'ordering': ['-order_num', 'id'],
                'abstract': False,
                'verbose_name': 'Rolling advertisement',
            },
        ),
    ]
