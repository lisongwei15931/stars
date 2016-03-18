#!/usr/bin/env python
# encoding: utf-8


import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from oscar.forms.widgets import ImageInput

from stars.apps.accounts.models import UserProfile, Captcha


def local_mobile_phone_validator(mobile_phone_number):
    phoneprefix=['130','131','132','133','134','135','136','137','138','139',
                 '150','151','152','153','156','158','159','170', '171', '172',
                 '178','181', '182','183','185','186','187','188','189']
    validator_str = r'^\d{11}$'
    validator_engine = re.compile(validator_str)

    if mobile_phone_number:
        if validator_engine.match(mobile_phone_number) and mobile_phone_number[0:3] in phoneprefix:
            return True
        else:
            return False
    else:
        return False


def local_identification_card_number_validator(identification_card_number):
    validator_str = '^(\d{6})(\d{4})(\d{2})(\d{2})(\d{3})([0-9]|X)$'
    validator_engine = re.compile(validator_str)

    if identification_card_number:
        if validator_engine.match(identification_card_number):
            return True
        else:
            return False
    else:
        return True


def local_phone_validator(phone_number):
    validator_str = r'(^(\d{11})$|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8}))$)'
    validator_engine = re.compile(validator_str)

    if phone_number:
        if validator_engine.match(phone_number):
            return True
        else:
            return False
    else:
        return True


class RegisterForm(forms.Form):
    username = forms.CharField(label=u'用户名', max_length=64, required=True,
            widget = forms.TextInput(attrs = {"onfocus": "OnfocusFun(this,'请输入用户名,6-20位字母数字')",
                                        "onblur": "OnBlurFun(this, '请输入用户名,6-20位字母数字')"}))
    password = forms.CharField(label=u'密码', max_length=64, required=True,
                               widget=forms.PasswordInput)
    re_password = forms.CharField(label=u'确认密码', max_length=64, required=True,
                                  widget=forms.PasswordInput)
    mobile_phone = forms.CharField(label=u'手机号', max_length=11, required=True,
                                   widget=forms.TextInput(attrs={'class': 'input-short'}))
    captcha = forms.CharField(label=u'验证码', max_length=32, required=True,
                              widget=forms.TextInput(attrs={'class': 'input-short'}))
    email = forms.EmailField(label=u'邮箱', required=False)
    introducer = forms.CharField(label=u'推荐人', max_length=64, required=False)
    user_agreement = forms.ChoiceField(label=u'用户协议', required=True,
                                       choices=((True, True), (False, False)),
                                       widget=forms.CheckboxInput(attrs={'checked':True}))

    def clean_username(self):
        data = self.cleaned_data['username']
        if data:
            try:
                user = User.objects.get(username=data)
                raise forms.ValidationError(u'用户名被占用。')
            except User.DoesNotExist:
                return data
        else:
            raise forms.ValidationError(u'用户名不可为空。')

    def clean_introducer(self):
        data = self.cleaned_data['introducer']
        if data:
            try:
                user = User.objects.get(username=data)
                return data
            except User.DoesNotExist:
                raise forms.ValidationError(u'没有这个用户，请重新输入。')
        return data

    def clean_re_password(self):
        cleaned_data = self.cleaned_data
        if 'password' in cleaned_data and 're_password' in cleaned_data:
            data = cleaned_data['re_password']
            password = cleaned_data['password']
            if password != data:
                raise forms.ValidationError(u'两次输入的密码不一致。')
        return cleaned_data

    def clean_mobile_phone(self):
        data = self.cleaned_data['mobile_phone']
        if not local_mobile_phone_validator(data):
            raise forms.ValidationError(u'手机号码不合法。')
        try:
            userprofile = UserProfile.objects.get(mobile_phone=data)
            raise forms.ValidationError(u'此号码已经被注册。')
        except UserProfile.DoesNotExist:
            pass
        return data

    def clean_captcha(self):
        cleaned_data = self.cleaned_data
        if 'mobile_phone' in cleaned_data:
            data = cleaned_data['captcha']
            mobile_phone = cleaned_data['mobile_phone']
            try:
                current_mobile_captcha = Captcha.objects.get(recipient=mobile_phone)
                if current_mobile_captcha.captcha != data:
                    raise forms.ValidationError(u'验证码不正确。')
            except Captcha.DoesNotExist:
                raise forms.ValidationError(u'验证码不正确。')
        else:
            if not self.data['mobile_phone']:
                raise forms.ValidationError(u'必须填手机号。')
        return cleaned_data

    def clean_email(self):
        data = self.cleaned_data['email']
        if data:
            try:
                user = User.objects.get(email=data)
                raise forms.ValidationError(u'此邮箱被占用。')
            except User.DoesNotExist:
                return data
        return data

    def clean_user_agreement(self):
        data = self.cleaned_data['user_agreement']
        if data == 'False':
            raise forms.ValidationError(u'必须同意用户协议。')
        return data


class IdentityForm(forms.ModelForm):
    '''
    real_name = forms.CharField(label=u'姓名', max_length=64, required=True)
    identification_card_number = forms.CharField(label=u'姓名', max_length=32, required=True)
    identification_card_image_front = forms.ImageField(upload_to='identification_card',
                                                        blank=True, null=True, verbose_name=u'身份证正面图')
    identification_card_image_back = forms.ImageField(upload_to='identification_card',
                                                       blank=True, null=True, verbose_name=u'身份证背面图')
    '''
    def __init__(self, *args, **kwargs):
        super(IdentityForm, self).__init__(*args, **kwargs)
        self.fields["real_name"].required = True
        self.fields["identification_card_number"].required = True
        self.fields["identification_card_image_front"].required = True
        self.fields["identification_card_image_back"].required = True

    class Meta:
        model = UserProfile
        fields = ['real_name', 'identification_card_number',
                  'identification_card_image_front', 'identification_card_image_back']
        '''
        widgets = {
            'identification_card_image_front': ImageInput(),
            'identification_card_image_back': ImageInput(),
        }
        '''

    def clean_identification_card_number(self):
        data = self.cleaned_data['identification_card_number']
        if not local_identification_card_number_validator(data):
            raise forms.ValidationError(u'身份证号码不合法。')
        return data


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=u'用户名', max_length=64, required=True,
                               widget=forms.TextInput(attrs={'class': 'login-f-txtstyle',
                                                             "onfocus": "OnfocusFun(this, '请输入用户名')",
                                                             "onblur": "OnBlurFun(this, '请输入用户名')"}))
    password = forms.CharField(label=u'密码', max_length=64, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'login-f-txtstyle',
                                                                 "onfocus": "OnfocusFun1(this, '请输入密码')",
                                                                 "onblur": "OnBlurFun1(this, '请输入密码')"}))

class ForgetPwForm(forms.Form):
    mobile_phone = forms.CharField(label=u'手机号', max_length=11, required=True,
                                   widget=forms.TextInput(attrs={'class': 'input-short'}))

    captcha = forms.CharField(label=u'验证码', max_length=32, required=True,
                              widget=forms.TextInput(attrs={'class': 'input-short'}))

    def clean_mobile_phone(self):
        data = self.cleaned_data['mobile_phone']

        if not local_mobile_phone_validator(data):
            raise forms.ValidationError(u'手机号码不合法。')
        try:
            userprofile = UserProfile.objects.get(mobile_phone=data)
        except:
            raise forms.ValidationError(u'此号码不为注册手机号。')
        return data


    def clean_captcha(self):
        cleaned_data = self.cleaned_data

        if 'mobile_phone' in cleaned_data:
            data = cleaned_data['captcha']
            mobile_phone = cleaned_data['mobile_phone']
            try:
                current_mobile_captcha = Captcha.objects.get(recipient=mobile_phone)
                if current_mobile_captcha.captcha != data:
                    print '*****'
                    print current_mobile_captcha.captcha
                    print '*****'
                    raise forms.ValidationError(u'验证码不正确。')
            except Captcha.DoesNotExist:
                raise forms.ValidationError(u'验证码不正确。')
        else:
            raise forms.ValidationError(u'验证码不正确。')

        return cleaned_data['captcha']

class ResetPwForm(forms.Form):
    password = forms.CharField(label=u'新密码', max_length=64, required=True,
                               widget=forms.PasswordInput(attrs = {"onfocus": "OnfocusFun1(this, '请输入密码')",
                                                                   "onblur" : "OnBlurFun1(this, '请输入密码')" ,
                                                                   "onkeyup":"pwStrength(this.value)" ,
                                                                   }))
    re_password = forms.CharField(label=u'确认密码', max_length=64, required=True,
                                  widget=forms.PasswordInput(attrs = {"onfocus": "OnfocusFun1(this, '重新输入密码')",
                                                                      "onblur" : "OnBlurFun1(this, '重新输入密码')" ,
                                                                      }))

    def clean_re_password(self):
        cleaned_data = self.cleaned_data
        if 'password' in cleaned_data and 're_password' in cleaned_data:
            data = cleaned_data['re_password']
            password = cleaned_data['password']
            if password != data:
                raise forms.ValidationError(u'两次输入的密码不一致。')
        return cleaned_data['re_password']


