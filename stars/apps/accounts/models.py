# -*- coding: utf-8 -*-s

import random

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings

from stars.apps.address.models import District
from stars.apps.accounts.role_validate import is_specific_role


ROLE_CHOICE = (('member', u'会员'), ('ISP', u'厂商'), ('dashboard_admin', u'后台管理员'),
        ('warehouse_staff', u'仓库人员'), ('member_unit', u'会员单位'),
        ('trader', u'交易员'))


class UserProfile(models.Model):
    VERIFIED_STATUS_CHOICE=((0, u'未认证'),(1, u'认证中'),(2, u'认证成功'),(3, u'认证失败'))
    SEX_CHOICE=((1, u'男'),(2, u'女'), (3, u'保密'))
    CERT_TYPE_CHOICE=((0, u'身份证'),(1, u'组织机构代码'))
    user = models.OneToOneField(User, verbose_name=u'用户')
    uid = models.IntegerField(blank=True, null=True, verbose_name='uid')
    username_checked = models.BooleanField(default=False, verbose_name='是否修改过用户名')
    funds_password = models.CharField(max_length=128, blank=True, null=True,
                                      verbose_name=u'资金密码')
    mobile_phone = models.CharField(max_length=15, unique=True,
                                    verbose_name=u'手机号码')
    avatar = models.ImageField(upload_to=settings.AVATAR_ROOT, blank=True, null=True,
                               verbose_name=u'头像')
    real_name = models.CharField(max_length=127, default='', blank=True, null=True,
                                 verbose_name=u'真实姓名')
    cert_type = models.SmallIntegerField(choices=CERT_TYPE_CHOICE, default=0, blank=True,null=True,
                                         verbose_name=u'证件类型')
    identification_card_number = models.CharField(max_length=32, blank=True,
                                                  null=True, verbose_name=u'身份证号')
    identification_card_image_front = models.ImageField(upload_to='identification_card',
                                                        blank=True, null=True, verbose_name=u'身份证正面图')
    identification_card_image_back = models.ImageField(upload_to='identification_card',
                                                       blank=True, null=True, verbose_name=u'身份证背面图')
    role = models.CharField(max_length=100, choices=ROLE_CHOICE, verbose_name=u'角色',
                            default='member')
    nickname = models.CharField(max_length=127, default='', blank=True, null=True,
                                 verbose_name=u'昵称')
    sex = models.PositiveSmallIntegerField(default=3, choices=SEX_CHOICE, verbose_name=u'性别')
    birthday = models.DateField(blank=True, null=True)
    interest = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u'兴趣')
    region = models.ForeignKey(District, verbose_name=u'地区', null=True, blank=True)
    address = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u'详细地址')

    # audit_status = models.BooleanField(default=False, verbose_name=u'审核通过状态')

    audit_status = models.PositiveSmallIntegerField(default=0, choices=VERIFIED_STATUS_CHOICE, verbose_name=u'认证状态')

    pay_pwd = models.CharField(blank=True, null=True, max_length=128, verbose_name=u'资金密码')
    pickup_pwd = models.CharField(blank=True, null=True, max_length=128, verbose_name=u'提货密码')
    desc = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name=u'备注')
    introducer = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'推荐人')
    register_ip = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'注册IP')
    created_date = models.DateField(auto_now_add=True, db_index=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'用户额外信息'

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return settings.DEFAULT_AVATAR

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.role != 'member':
            self.user.is_staff = True
            self.user.save()
        if not self.uid:
            self.uid = self.user.id + 10000000
        super(UserProfile, self).save(*args, **kwargs)

    def is_dashboard_admin(self):
        return is_specific_role(self.user, 'dashboard_admin')

    def is_ISP(self):
        return is_specific_role(self.user, 'ISP')

    def is_warehouse_staff(self):
        return is_specific_role(self.user, 'warehouse_staff')

    def is_member_unit(self):
        return is_specific_role(self.user, 'member_unit')

    def is_trader(self):
        return is_specific_role(self.user, 'trader')


def save_additional_info(sender, **kwargs):
    current_user = kwargs['instance']
    try:
        current_userprofile = current_user.userprofile
    except UserProfile.DoesNotExist:
        exist_mobile_phone = True
        while exist_mobile_phone:
            new_mobile_phone = random.randint(10000000000, 99999999999)
            try:
                current_userprofile = UserProfile.objects.get(mobile_phone=new_mobile_phone)
            except UserProfile.DoesNotExist:
                exist_mobile_phone = False
        UserProfile.objects.create(user=current_user, mobile_phone=new_mobile_phone)


post_save.connect(receiver=save_additional_info, sender=User, weak=False)


class Captcha(models.Model):
    recipient = models.CharField(max_length=32, unique=True, verbose_name=u'手机号码')
    captcha = models.CharField(max_length=15, verbose_name=u'验证码')
    deadline_time = models.DateTimeField(blank=True, null=True, verbose_name=u'过期时间')

    class Meta:
        verbose_name = verbose_name_plural = u'验证码'

    def __unicode__(self):
        return self.recipient
