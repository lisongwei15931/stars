# -*- coding: utf-8 -*-

from django import forms
from stars.apps.customer.assets.utils import is_valid_mobile, is_valid_bank_card_num, is_valid_bank


class UserInfoForm(forms.Form):

    nickname = forms.CharField(max_length=100)
    sex = forms.RadioSelect()
    birthday = forms.DateField()
    interest = forms.Textarea()
    real_name = forms.CharField()
    mobile_phone = forms.CharField()
    email = forms.EmailField(label=u'邮箱')

    address = forms.CharField()

    region = forms.IntegerField()


