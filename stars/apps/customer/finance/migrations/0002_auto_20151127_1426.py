# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.db import migrations

from stars.apps.customer.finance.ab import ab_util


def init_AgriculturalBankOriginalKey(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    k = apps.get_model("finance", "AgriculturalBankOriginalKey")
    if not k.objects.exists():
        k(package=ab_util.ori_pack_key, pin= ab_util.ori_pin_key, mac=ab_util.ori_mac_key).save()

def init_AgriculturalBankEncKey(apps, schema_editor):
    k = apps.get_model("finance", "AgriculturalBankEncKey")
    if not k.objects.exists():
        k(package=ab_util._init_pack_key, pin= ab_util._init_pin_key, mac=ab_util._init_mac_key,
          expire_time=datetime.now()+timedelta(days=365)).save()


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_AgriculturalBankOriginalKey),
        migrations.RunPython(init_AgriculturalBankEncKey),
    ]
