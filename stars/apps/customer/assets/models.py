# -*- coding: utf-8 -*-

from django.db import models
from oscar.core.compat import AUTH_USER_MODEL


# class UserAssets(models.Model):
#     """
#     用户账户
#     """
#     user = models.OneToOneField(AUTH_USER_MODEL, verbose_name=u'用户')
#     balance = models.PositiveIntegerField(verbose_name=u'账户余额', default=0)  # 单位：分
#     modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)
#
#     class Meta:
#         app_label = 'assets'
#
# class BankCard(models.Model):
#     """
#     银行卡
#     """
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=u'用户')
#     bank_account = models.CharField(max_length=30)
#     bank_name = models.CharField(max_length=100)
#     desc = models.CharField(max_length=200)
#     is_enable = models.BooleanField(default=True)
#
#     is_deleted = models.BooleanField(default=False)  #逻辑删除标识
#
#     created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
#     modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)
#
#     class Meta:
#         app_label = 'assets'


# class Withdrawal(models.Model):
#     """
#     提现
#     """
#     STATUS_CHOICES=((0, u'交易中'),(1, u'交易成功'),(2, u'交易失败'))
#
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=u'用户')
#     amount = models.PositiveIntegerField(verbose_name=u'金额')  #单位：分
#     status = models.IntegerField(verbose_name=u'状态', choices=STATUS_CHOICES, default=0)
#     user_account = models.IntegerField(verbose_name=u'对方', default=-1) # 提现到的银行账户
#     user_account_desc = models.CharField(max_length=100, default='')
#     comment = models.CharField(max_length=200, default='')
#
#     created_time = models.DateTimeField(verbose_name=(u'生成时间'), auto_now_add=True, editable=False)
#     modified_time = models.DateTimeField(verbose_name=(u'修改时间'), auto_now=True, editable=False)
#
#     class Meta:
#         app_label = 'assets'
#
#
# class Deposit(models.Model):
#     """
#     充值
#     """
#     STATUS_CHOICES=((0, u'交易中'),(1, u'交易成功'),(2, u'交易失败'))
#
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=u'用户')
#     amount = models.PositiveIntegerField(verbose_name=u'金额')  #单位：分
#     status = models.IntegerField(verbose_name=u'状态', choices=STATUS_CHOICES, default=0)
#     user_account = models.IntegerField(verbose_name=u'对方', default=-1)  # 充值的银行账户
#     user_account_desc = models.CharField(max_length=100, default='')
#     comment = models.CharField(max_length=200, default='')
#
#     created_time = models.DateTimeField(verbose_name=(u'生成时间'), auto_now_add=True, editable=False)
#     modified_time = models.DateTimeField(verbose_name=(u'修改时间'), auto_now=True, editable=False)
#
#     class Meta:
#         app_label = 'assets'
