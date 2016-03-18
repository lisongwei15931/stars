# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_auto_20151205_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbBankStatement',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('trans_date', models.DateField(verbose_name='\u4ea4\u6613\u65e5\u671f', editable=False)),
                ('trans_time', models.TimeField(verbose_name='\u4ea4\u6613\u65f6\u95f4', null=True, editable=False, blank=True)),
                ('bank_account', models.CharField(default=b'', max_length=30)),
                ('source_side', models.CharField(blank=True, max_length=6, null=True, choices=[(b'B', '\u94f6\u884c'), (b'I', '\u5e02\u573a')])),
                ('trans_code', models.CharField(max_length=20)),
                ('serial_no', models.CharField(max_length=60, db_index=True)),
                ('inst_serial', models.CharField(default=b'', unique=True, max_length=60, blank=True)),
                ('amount', models.DecimalField(max_digits=30, decimal_places=5)),
                ('client_no', models.CharField(max_length=20)),
                ('inst_no', models.CharField(max_length=30)),
                ('busi_type', models.CharField(default=b'6', max_length=6, choices=[(b'6', '\u4fdd\u8bc1\u91d1'), (b'7', '\u8d37\u6b3e')])),
                ('money_kind', models.CharField(default=b'01', max_length=6)),
                ('inst_func_acc', models.CharField(max_length=30)),
                ('user_id', models.IntegerField()),
                ('charge', models.DecimalField(max_digits=30, decimal_places=5)),
                ('reserve1', models.CharField(default=b'', max_length=300)),
                ('reserve2', models.CharField(default=b'', max_length=300)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u751f\u6210\u65f6\u95f4')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='AbRechargeWithdrawErrorStatus',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('status', models.IntegerField(choices=[(1, '\u94f6\u884c\u6210\u529f\u5e02\u573a\u5931\u8d25'), (2, '\u94f6\u884c\u5931\u8d25\u5e02\u573a\u6210\u529f'), (3, '\u94f6\u884c\u5e02\u573a\u91d1\u989d\u4e0d\u5339\u914d')])),
                ('result', models.IntegerField(default=1, choices=[(1, '\u672a\u5904\u7406'), (2, '\u5904\u7406\u4e2d'), (3, '\u5df2\u4fee\u6b63')])),
                ('fixed_user', models.CharField(default=b'', max_length=20)),
                ('fixed_event', models.CharField(default=b'', max_length=20)),
                ('fixed_comment', models.CharField(default=b'', max_length=500)),
                ('fixed_time', models.DateTimeField(verbose_name='\u4fee\u6b63\u65f6\u95f4', null=True, editable=False, blank=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u751f\u6210\u65f6\u95f4')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('bank_statement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='finance.AbBankStatement', null=True)),
                ('market_statement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='finance.AbRechargeWithdrawLog', null=True)),
            ],
        ),
    ]
