# -*- coding: utf-8 -*-

from django import forms
from stars.apps.commission.models import UserBank

from stars.apps.customer.assets.utils import is_valid_mobile, is_valid_bank_card_num, is_valid_bank


class BankCardForm(forms.ModelForm):

    def __init__(self, user,*args, **kwargs):
        self.user = user
        super(self.__class__, self).__init__(*args, **kwargs)
        # self.fields["user_name"].required = True
        # self.fields["id_card"].required = True
        # self.user = user
        self.fields["bank_name"].required = True
        self.fields["bank_account"].required = True
        self.fields["tel"].required = True

    class Meta:
        model = UserBank
        fields = [ 'bank_name', 'bank_account',
                  'tel',]

    def clean_vcode(self):
        data = self.cleaned_data['vcode']
        if not data:
            raise forms.ValidationError(u'这个字段是必填项。')
        return data

    def clean_bank_account(self):
        data = self.cleaned_data['bank_account']
        if not is_valid_bank_card_num(data):
            raise forms.ValidationError(u'卡号不合法。')
        return data

    def clean_bank_name(self):
        data = self.cleaned_data['bank_name']
        if not is_valid_bank(data):
            raise forms.ValidationError(u'不支持该银行。')
        return data

    def clean_tel(self):
        data = self.cleaned_data['tel']
        if not is_valid_mobile(data):
            raise forms.ValidationError(u'手机号不合法。')
        return data

    def save(self, *args, **kwargs):

        super(self.__class__, self).save(*args,**kwargs) # Call the "real" save() method.
