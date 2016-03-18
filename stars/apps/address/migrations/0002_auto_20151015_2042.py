# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u57ce\u5e02\u540d')),
                ('slug_name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': '\u57ce\u5e02',
                'verbose_name_plural': '\u57ce\u5e02',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u533a\u540d')),
                ('slug_name', models.CharField(max_length=64)),
                ('city', models.ForeignKey(verbose_name='\u6240\u5c5e\u57ce\u5e02', to='address.City')),
            ],
            options={
                'verbose_name': '\u533a',
                'verbose_name_plural': '\u533a',
            },
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u7701\u540d')),
                ('slug_name', models.CharField(unique=True, max_length=64)),
            ],
            options={
                'verbose_name': '\u7701',
                'verbose_name_plural': '\u7701',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='province',
            field=models.ForeignKey(verbose_name='\u6240\u5c5e\u7701', to='address.Province'),
        ),
        migrations.AlterUniqueTogether(
            name='district',
            unique_together=set([('slug_name', 'city')]),
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together=set([('slug_name', 'province')]),
        ),
    ]
