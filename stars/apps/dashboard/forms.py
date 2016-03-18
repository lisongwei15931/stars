# -*- coding: utf-8 -*-s


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class LoginForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                self._errors['password'] = self.error_class([u'用户名/密码错误'])
            elif not self.user_cache.is_active:
                self._errors['username'] = self.error_class([u'此用户已经被删除'])
            elif not self.user_cache.is_staff:
                self._errors['username'] = self.error_class([u'您无权登录管理平台'])
            else:
                try:
                    current_userprofile = self.user_cache.userprofile
                    if not current_userprofile.is_dashboard_admin():
                        self._errors['username'] = self.error_class([u'您不是后台管理员'])
                except:
                    self._errors['username'] = self.error_class([u'您无权登录管理平台'])

        return self.cleaned_data
