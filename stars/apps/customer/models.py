# -*- coding: utf-8 -*-

from safety.models import *


# class IncomeLog(models.Model):
#     """
#     用户收支日志
#     """
#     EVENT_CHOICES=((1, u'充值'),(2, u'提现'))
#     STATUS_CHOICES=((0, u'交易中'),(1, u'交易成功'),(2, u'交易失败'))
#
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=u'用户')
#     amount = models.IntegerField(verbose_name=u'金额')
#     event = models.IntegerField(verbose_name=u'类型', choices=EVENT_CHOICES)
#     status = models.IntegerField(verbose_name=u'状态', choices=STATUS_CHOICES, default=0)
#     to = models.IntegerField(verbose_name=u'对方', default=-1)
#     to_desc = models.CharField(max_length=100, default='')
#     comment = models.CharField(max_length=200, default='')
#
#     created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
#     modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)
#
#     class Meta:
#         app_label = 'customer'


from oscar.apps.customer.models import *  # noqa
