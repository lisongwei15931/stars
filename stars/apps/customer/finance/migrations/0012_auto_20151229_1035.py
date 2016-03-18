# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0011_alipaymentbill_alipaymenttradeorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='abrechargewithdrawhistory',
            name='cash_ex_code',
            field=models.CharField(default=b'2', max_length=10),
        ),
        migrations.AddField(
            model_name='abrechargewithdrawlog',
            name='cash_ex_code',
            field=models.CharField(default=b'2', max_length=10),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_address',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_email',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_fax_no',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_gender',
            field=models.CharField(default=b'', max_length=4, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_mobile',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_nationality',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_postcode',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='agent_tel_no',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='gender',
            field=models.CharField(default=b'', max_length=4, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='absignincontractlog',
            name='nationality',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
        ),
    ]
