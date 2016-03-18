# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from oscar.core.compat import AUTH_USER_MODEL


class MailVerificationCode(models.Model):
    """
    邮箱验证
    """
    STATUS_CHOICES=((0, u'有效'),(1, u'使用'),(2, u'失效'))
    TYPE_CHOICES=((1, u'绑定邮箱验证'),(2, u'修改邮箱验证'),(3, u'解绑邮箱验证'))

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=40)
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=u'用户')
    type = models.IntegerField(verbose_name=u'类型', choices=TYPE_CHOICES)
    status = models.IntegerField(verbose_name=u'状态', choices=STATUS_CHOICES, default=0)
    data = models.CharField(max_length=100, default='')  #修改邮箱时，保存新邮箱地址
    comment = models.CharField(max_length=200, default='')

    created_time = models.DateTimeField(verbose_name=_(u'生成时间'), auto_now_add=True, editable=False)
    expired_time = models.DateTimeField(verbose_name=_(u'过期时间'), editable=False)
    modified_time = models.DateTimeField(verbose_name=_(u'修改时间'), auto_now=True, editable=False)

    class Meta:
        app_label = 'safety'


class SmsVerificationCode(models.Model):
    """
    手机短信验证
    """
    STATUS_CHOICES=((0, u'有效'),(1, u'使用'),(2, u'失效'))
    TYPE_CHOICES=((1, u'修改手机号码-验证旧手机'),
                  (2, u'修改手机号码-验证新手机'),
                  (3, u'修改资金密码'),
                  (4, u'修改邮箱'),
                  (5, u'修改登录密码'),
                  (6, u'验证手机'),
                  (7, u'解绑银行卡'),
                  )

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10)
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=u'用户')
    type = models.IntegerField(verbose_name=u'类型', choices=TYPE_CHOICES)
    status = models.IntegerField(verbose_name=u'状态', choices=STATUS_CHOICES, default=0)
    data = models.CharField(max_length=100, default='')  # 保存手机号
    comment = models.CharField(max_length=200, default='')

    created_time = models.DateTimeField(verbose_name=_(u'生成时间'), auto_now_add=True, editable=False)
    expired_time = models.DateTimeField(verbose_name=_(u'过期时间'), editable=False)
    modified_time = models.DateTimeField(verbose_name=_(u'修改时间'), auto_now=True, editable=False)

    class Meta:
        app_label = 'safety'


# class PaymentPassword(models.Model):
#     """
#     用户账户
#     """
#     user = models.OneToOneField(AUTH_USER_MODEL, verbose_name=u'用户')
#     password = models.CharField(max_length=100)
#
#     created_time = models.DateTimeField(verbose_name=_(u'生成时间'), auto_now_add=True, editable=False)
#     modified_time = models.DateTimeField(verbose_name=_(u'修改时间'), auto_now=True, editable=False)
#
#     class Meta:
#         app_label = 'safety'
#
#     def set_password(self, raw_password):
#         self.password = make_password(raw_password)
#
#     def check_password(self, raw_password):
#         """
#         判断密码是否正确
#         """
#         return check_password(raw_password, self.password, None)
