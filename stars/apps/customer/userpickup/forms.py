#coding=utf-8


from stars.apps.commission.models import UserPickupAddr
from django import forms
from stars.apps.accounts.forms import (local_mobile_phone_validator,
                                       local_phone_validator)

class UserPickupForm(forms.ModelForm):
    class Meta:
        model= UserPickupAddr
        exclude = ['user',]
        
        widgets = {
                  'pickup_addr' :forms.TextInput(attrs={'name':"pickup_address_id" ,'id':"pickup_address_id"}),
                  }


#===============================================================================
# #自提点forms    
# class UserPickupContactForm(forms.ModelForm):
#     class Meta :
#         model = UserPickupContact
#         exclude = ['user',]
#         widget = {
#                   'name': forms.TextInput(attrs={'class':'input-short'}),
#                   'tel' : forms.TextInput(attrs={'class':'input-short'}),
#                   'id_card_no' : forms.TextInput(attrs={'class':'input-short'}),
#                   'plate_number' : forms.TextInput(attrs={'class':'input-short'}),  
#                   }
#         
#     def clean_tel(self):
#         data = self.cleaned_data['tel']
# 
#         if not local_phone_validator(data):
#             raise forms.ValidationError(u'电话号码不合法。')
#         if not local_phone_validator(data):
#             raise forms.ValidationError(u'手机号码不合法')
#         return data  
#     
#===============================================================================