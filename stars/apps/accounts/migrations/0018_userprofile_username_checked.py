# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_userprofile_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='username_checked',
            field=models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe4\xbf\xae\xe6\x94\xb9\xe8\xbf\x87\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d'),
        ),
    ]
