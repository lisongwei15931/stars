# -*- coding: utf-8 -*-s

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Province(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'省名')
    slug_name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = verbose_name_plural = u'省'

    def __unicode__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'城市名')
    slug_name = models.CharField(max_length=64)
    province = models.ForeignKey(Province, verbose_name=u'所属省')
    lat = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'纬度')
    lng = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'经度')

    class Meta:
        verbose_name = verbose_name_plural = u'城市'
        unique_together = (('slug_name', 'province'),)

    def __unicode__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'区名')
    slug_name = models.CharField(max_length=64)
    city = models.ForeignKey(City, verbose_name=u'所属城市')
    lat = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'纬度')
    lng = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'经度')

    class Meta:
        verbose_name = verbose_name_plural = u'区'
        unique_together = (('slug_name', 'city'),)

    def __unicode__(self):
        return self.name


class ReceivingAddress(models.Model):
    user = models.ForeignKey(User, verbose_name=u'用户')
    consignee = models.CharField(max_length=64, verbose_name=u'收货人')
    province = models.ForeignKey(Province, verbose_name=u'所属省')
    city = models.ForeignKey(City, verbose_name=u'所属城市')
    district = models.ForeignKey(District, verbose_name=u'所属区')
    address = models.CharField(max_length=255, verbose_name=u'详细地址')
    mobile_phone = models.CharField(max_length=15, verbose_name=u'手机号码')
    telephone = models.CharField(max_length=15, verbose_name=u'固定电话',
                                 blank=True, null=True)
    email = models.EmailField(verbose_name=u'邮箱', blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name=u'是否为默认地址')

    class Meta:
        verbose_name = verbose_name_plural = u'收货地址'

    def __unicode__(self):
        return ' '.join([self.consignee, self.city.name])

    def save(self, *args, **kwargs):
        try:
            current_address = ReceivingAddress.objects.filter(user=self.user)
            current_address.get(is_default=True)
            if current_address and (self.is_default is True):
                current_address.update(is_default=False)
        except ReceivingAddress.DoesNotExist:
            pass
        except ReceivingAddress.MultipleObjectsReturned:
            current_address.exclude(id=self.id).update(is_default=False)
            self.is_default = True
        finally:
            super(ReceivingAddress, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_default:
            try:
                current_address = ReceivingAddress.objects.filter(user=self.user)
                if len(current_address) > 1:
                    new_default_address = current_address.exclude(id=self.id)[0]
                    new_default_address.is_default = True
                    new_default_address.save()
            except:
                pass
        super(ReceivingAddress, self).delete(*args, **kwargs)


from oscar.apps.address.models import *  # noqa
