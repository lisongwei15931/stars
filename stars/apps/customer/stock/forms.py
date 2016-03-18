#!/usr/bin/env python
# encoding: utf-8


from django import forms

from stars.apps.address.models import ReceivingAddress
from stars.apps.accounts.forms import (local_mobile_phone_validator,
                                       local_phone_validator)


class ReceivingAddressForm(forms.ModelForm):
    class Meta:
        model = ReceivingAddress
        exclude = ['user', ]
        widgets = {
            'province': forms.Select(attrs={'class':'input-group-select l'}),
            'city': forms.Select(attrs={'class':'input-group-select l'}),
            'district': forms.Select(attrs={'class':'input-group-select l'}),
            'address': forms.TextInput(attrs={'class':'input-long'}),
            'mobile_phone': forms.TextInput(attrs={'class':'input-short'}),
            'telephone': forms.TextInput(attrs={'class':'input-short'}),
            'email': forms.TextInput(attrs={'class':'input-short'}),
        }

    def clean_mobile_phone(self):
        data = self.cleaned_data['mobile_phone']

        if not local_mobile_phone_validator(data):
            raise forms.ValidationError(u'手机号码不合法。')
        return data

    def clean_telephone(self):
        data = self.cleaned_data['telephone']

        if not local_phone_validator(data):
            raise forms.ValidationError(u'电话号码不合法。')
        return data
