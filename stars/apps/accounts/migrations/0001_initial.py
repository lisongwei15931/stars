# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Captcha',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient', models.CharField(unique=True, max_length=32, verbose_name='\u624b\u673a\u53f7\u7801')),
                ('captcha', models.CharField(max_length=15, verbose_name='\u9a8c\u8bc1\u7801')),
            ],
            options={
                'verbose_name': '\u9a8c\u8bc1\u7801',
                'verbose_name_plural': '\u9a8c\u8bc1\u7801',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mobile_phone', models.CharField(unique=True, max_length=15, verbose_name='\u624b\u673a\u53f7\u7801')),
                ('avatar', models.ImageField(upload_to=b'avatar', null=True, verbose_name='\u5934\u50cf', blank=True)),
                ('real_name', models.CharField(max_length=127, null=True, verbose_name='\u771f\u5b9e\u59d3\u540d', blank=True)),
                ('identification_card_number', models.CharField(max_length=32, null=True, verbose_name='\u8eab\u4efd\u8bc1\u53f7', blank=True)),
                ('identification_card_image_front', models.ImageField(upload_to=b'identification_card', null=True, verbose_name='\u8eab\u4efd\u8bc1\u6b63\u9762\u56fe', blank=True)),
                ('identification_card_image_back', models.ImageField(upload_to=b'identification_card', null=True, verbose_name='\u8eab\u4efd\u8bc1\u80cc\u9762\u56fe', blank=True)),
                ('user', models.OneToOneField(verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u989d\u5916\u4fe1\u606f',
                'verbose_name_plural': '\u7528\u6237\u989d\u5916\u4fe1\u606f',
            },
        ),
    ]
