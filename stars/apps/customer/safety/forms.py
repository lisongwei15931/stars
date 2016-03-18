# -*- coding: utf-8 -*-

from django import forms

from stars.apps.accounts.models import UserProfile
from stars.apps.customer.safety.utils import is_valid_id_card_num


class RealNameAuthForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields["real_name"].required = True
        self.fields["identification_card_number"].required = True
        self.fields["identification_card_image_front"].required = True
        self.fields["identification_card_image_back"].required = True

    class Meta:
        model = UserProfile
        fields = ['real_name', 'identification_card_number',
                  'identification_card_image_front', 'identification_card_image_back']

    def clean_identification_card_number(self):
        data = self.cleaned_data['identification_card_number']
        if not is_valid_id_card_num(data):
            raise forms.ValidationError(u'身份证号码不合法。')
        return data

    def save(self, *args, **kwargs):
        # self.identification_card_image_front

        super(self.__class__, self).save(*args,**kwargs) # Call the "real" save() method.
