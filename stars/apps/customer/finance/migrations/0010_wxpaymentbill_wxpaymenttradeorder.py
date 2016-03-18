# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_abbankstatement_abrechargewithdrawerrorstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='WxPaymentBill',
            fields=[
                ('trade_no', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('wx_transaction_id', models.CharField(default=b'', max_length=100)),
                ('bill_type', models.CharField(max_length=10, choices=[(b'ALL', '\u8fd4\u56de\u5f53\u65e5\u6240\u6709\u8ba2\u5355\u4fe1\u606f\uff0c\u9ed8\u8ba4\u503c'), (b'SUCCESS', '\u8fd4\u56de\u5f53\u65e5\u6210\u529f\u652f\u4ed8\u7684\u8ba2\u5355'), (b'REFUND', '\u8fd4\u56de\u5f53\u65e5\u9000\u6b3e\u8ba2\u5355'), (b'REVOKED', '\u5df2\u64a4\u9500\u7684\u8ba2\u5355')])),
                ('trade_time', models.DateTimeField()),
                ('mch_id', models.CharField(max_length=32)),
                ('sub_mch_id', models.CharField(default=b'', max_length=32)),
                ('appid', models.CharField(max_length=32)),
                ('device_no', models.CharField(default=b'', max_length=32)),
                ('open_id', models.CharField(default=b'', max_length=128)),
                ('trade_type', models.CharField(default=b'', max_length=32)),
                ('trade_status', models.CharField(max_length=30)),
                ('bank_type', models.CharField(max_length=30)),
                ('fee_type', models.CharField(max_length=30)),
                ('total_fee', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('coupon_fee', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('refund_request_time', models.DateTimeField(null=True, blank=True)),
                ('refund_success_time', models.DateTimeField(null=True, blank=True)),
                ('wx_refund_no', models.CharField(default=b'', max_length=32)),
                ('mch_refund_no', models.CharField(default=b'', max_length=28)),
                ('refund_fee', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('refund_coupon_fee', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('refund_type', models.CharField(default=b'', max_length=50)),
                ('refund_status', models.CharField(default=b'', max_length=50)),
                ('trade_name', models.CharField(default=b'', max_length=200)),
                ('trade_attach', models.CharField(default=b'', max_length=200)),
                ('service_charges', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('rate', models.CharField(default=b'', max_length=20)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WxPaymentTradeOrder',
            fields=[
                ('trade_no', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('uid', models.IntegerField()),
                ('product_id', models.CharField(max_length=100)),
                ('device_info', models.CharField(default=b'WEB', max_length=100)),
                ('body', models.CharField(default=b'', max_length=40, blank=True)),
                ('detail', models.CharField(default=b'', max_length=300, blank=True)),
                ('attach', models.CharField(default=b'', max_length=150, blank=True)),
                ('transaction_id', models.CharField(default=b'', max_length=100)),
                ('total_fee', models.IntegerField()),
                ('spbill_create_ip', models.CharField(default=b'', max_length=30)),
                ('start_time', models.DateTimeField()),
                ('time_expire', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('trade_type', models.CharField(default=b'NATIVE', max_length=10)),
                ('limit_pay', models.CharField(default=b'no_credit', max_length=10, blank=True)),
                ('openid', models.CharField(default=b'', max_length=10, blank=True)),
                ('is_order_over', models.BooleanField(default=False)),
                ('order_status', models.SmallIntegerField(default=0, choices=[(0, '\u8fdb\u884c\u4e2d'), (1, '\u652f\u4ed8\u5931\u8d25'), (2, '\u9884\u652f\u4ed8\u4e2d'), (3, '\u652f\u4ed8\u6210\u529f'), (4, '\u672a\u652f\u4ed8'), (5, '\u5df2\u5173\u95ed'), (6, '\u5df2\u64a4\u9500'), (7, '\u7528\u6237\u652f\u4ed8\u4e2d'), (8, '\u8f6c\u5165\u9000\u6b3e'), (9, '\u7edf\u4e00\u4e0b\u5355\u5931\u8d25')])),
                ('order_status_desc', models.CharField(default=b'', max_length=200)),
                ('original_source', models.SmallIntegerField(choices=[(b'0', b'\xe7\xbd\x91\xe9\xa1\xb5\xe6\x89\xab\xe7\xa0\x81\xe6\x94\xaf\xe4\xbb\x98'), (b'1', b'android'), (b'2', b'ios')])),
                ('appid', models.CharField(max_length=32)),
                ('mch_id', models.CharField(max_length=32)),
                ('wx_return_code', models.CharField(default=b'', max_length=16, null=True, blank=True)),
                ('wx_return_msg', models.CharField(default=b'', max_length=200, null=True, blank=True)),
                ('wx_result_code', models.CharField(default=b'', max_length=16, null=True, blank=True)),
                ('wx_err_code', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('wx_err_code_des', models.CharField(default=b'', max_length=200, null=True, blank=True)),
                ('wx_prepay_id', models.CharField(default=b'', max_length=70, null=True, blank=True)),
                ('code_url', models.CharField(default=b'', max_length=70, null=True, blank=True)),
                ('code_url_img_path', models.CharField(default=b'', max_length=300, null=True, blank=True)),
                ('code_url_img_url', models.CharField(default=b'', max_length=300, null=True, blank=True)),
                ('wx_response', models.CharField(default=b'', max_length=1000, null=True, blank=True)),
                ('comment', models.CharField(default=b'', max_length=600)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('modification_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
