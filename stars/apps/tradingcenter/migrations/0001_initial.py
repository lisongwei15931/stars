# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_productattribute_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SelfPick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product', models.ForeignKey(related_name='self_pick_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='self_pick_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u81ea\u9009\u5217\u8868',
                'verbose_name_plural': '\u81ea\u9009\u5217\u8868',
            },
        ),
    ]
