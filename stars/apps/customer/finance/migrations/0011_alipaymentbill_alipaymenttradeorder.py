# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0010_wxpaymentbill_wxpaymenttradeorder'),
    ]

    operations = [
        migrations.CreateModel(
            name='AliPaymentBill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trans_date', models.DateTimeField()),
                ('transaction_id', models.CharField(default=b'', max_length=70, db_index=True)),
                ('merchant_out_order_no', models.CharField(default=b'', max_length=70, db_index=True)),
                ('trans_out_order_no', models.CharField(default=b'', max_length=70, db_index=True)),
                ('total_fee', models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)),
                ('trade_refund_amount', models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)),
                ('balance', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('income', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('outcome', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('partner_id', models.CharField(default=b'', max_length=40)),
                ('sub_trans_code_msg', models.CharField(default=b'', max_length=30)),
                ('trans_code_msg', models.CharField(default=b'', max_length=100, blank=True)),
                ('bank_name', models.CharField(default=b'', max_length=50)),
                ('bank_account_no', models.CharField(default=b'', max_length=40)),
                ('bank_account_name', models.CharField(default=b'', max_length=40)),
                ('memo', models.CharField(default=b'', max_length=200)),
                ('buyer_account', models.CharField(default=b'', max_length=60)),
                ('seller_account', models.CharField(default=b'', max_length=60)),
                ('seller_fullname', models.CharField(default=b'', max_length=60)),
                ('currency', models.CharField(default=b'', max_length=10)),
                ('deposit_bank_no', models.CharField(default=b'', max_length=100)),
                ('goods_title', models.CharField(default=b'', max_length=200)),
                ('iw_account_log_id', models.CharField(default=b'', max_length=100)),
                ('trans_account', models.CharField(default=b'', max_length=100)),
                ('other_account_email', models.CharField(default=b'', max_length=100)),
                ('other_account_fullname', models.CharField(default=b'', max_length=100)),
                ('other_user_id', models.CharField(default=b'', max_length=100)),
                ('service_fee', models.CharField(default=b'', max_length=100)),
                ('service_fee_ratio', models.CharField(default=b'', max_length=20)),
                ('sign_product_name', models.CharField(default=b'', max_length=128)),
                ('rate', models.CharField(default=b'', max_length=20)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AliPaymentTradeOrder',
            fields=[
                ('out_trade_no', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('uid', models.IntegerField()),
                ('order_no', models.CharField(max_length=100)),
                ('payment_type', models.CharField(default=b'1', max_length=4)),
                ('seller_id', models.CharField(max_length=16)),
                ('seller_email', models.CharField(max_length=100)),
                ('seller_account_name', models.CharField(max_length=100)),
                ('subject', models.CharField(default=b'', max_length=40, blank=True)),
                ('body', models.CharField(default=b'', max_length=300, blank=True)),
                ('extra_common_param', models.CharField(default=b'', max_length=100, blank=True)),
                ('extend_param', models.CharField(default=b'', max_length=100, blank=True)),
                ('it_b_pay', models.CharField(default=b'', max_length=10, blank=True)),
                ('total_fee', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('notify_id', models.CharField(default=b'', max_length=100, blank=True)),
                ('notify_time', models.CharField(default=b'', max_length=30, blank=True)),
                ('notify_type', models.CharField(default=b'', max_length=30, blank=True)),
                ('gmt_create', models.DateTimeField(null=True, blank=True)),
                ('gmt_payment', models.DateTimeField(null=True, blank=True)),
                ('gmt_close', models.DateTimeField(null=True, blank=True)),
                ('gmt_last_modified_time', models.DateTimeField(null=True, blank=True)),
                ('time_out', models.DateTimeField(null=True, blank=True)),
                ('time_out_type', models.CharField(default=b'', max_length=30, blank=True)),
                ('refund_status', models.CharField(default=b'', max_length=30, blank=True)),
                ('gmt_refund', models.DateTimeField(null=True, blank=True)),
                ('refund_total_fee', models.IntegerField(default=0)),
                ('buyer_id', models.CharField(default=b'', max_length=30, blank=True)),
                ('buyer_email', models.CharField(default=b'', max_length=100, blank=True)),
                ('agent_user_id', models.CharField(default=b'', max_length=30, blank=True)),
                ('transaction_id', models.CharField(default=b'', max_length=100)),
                ('start_time', models.DateTimeField()),
                ('ali_service', models.CharField(default=b'create_direct_pay_by_user', max_length=50, blank=True)),
                ('is_order_over', models.BooleanField(default=False)),
                ('order_status', models.SmallIntegerField(default=0, choices=[(0, '\u8fdb\u884c\u4e2d'), (1, '\u652f\u4ed8\u5931\u8d25'), (2, '\u9884\u652f\u4ed8\u4e2d'), (3, '\u4ea4\u6613\u6210\u529f\uff0c\u4e14\u53ef\u5bf9\u8be5\u4ea4\u6613\u505a\u64cd\u4f5c\uff0c\u5982\uff1a\u591a\u7ea7\u5206\u6da6\u3001\u9000\u6b3e\u7b49'), (9, '\u4ea4\u6613\u6210\u529f\u4e14\u7ed3\u675f\uff0c\u4e0d\u53ef\u518d\u505a\u4efb\u4f55\u64cd\u4f5c'), (10, '\u7b49\u5f85\u5356\u5bb6\u6536\u6b3e\uff08\u4e70\u5bb6\u4ed8\u6b3e\u540e\uff0c\u5982\u679c\u5356\u5bb6\u8d26\u53f7\u88ab\u51bb\u7ed3\uff09'), (101, '\u8f6c\u5165\u9000\u6b3e'), (102, '\u9000\u6b3e\u6210\u529f'), (103, '\u9000\u6b3e\u5173\u95ed')])),
                ('ali_return_code', models.CharField(default=b'', max_length=16, null=True, blank=True)),
                ('ali_return_msg', models.CharField(default=b'', max_length=200, null=True, blank=True)),
                ('ali_result_code', models.CharField(default=b'', max_length=16, null=True, blank=True)),
                ('ali_err_code', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('ali_err_code_des', models.CharField(default=b'', max_length=200, null=True, blank=True)),
                ('ali_trade_status', models.CharField(default=b'', max_length=100, blank=True)),
                ('ali_response', models.CharField(default=b'', max_length=1000, null=True, blank=True)),
                ('comment', models.CharField(default=b'', max_length=600)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('modification_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
