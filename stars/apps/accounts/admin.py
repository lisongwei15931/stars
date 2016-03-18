# -*- coding: utf-8 -*-s

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from stars.apps.accounts.models import (UserProfile, Captcha)


class AdminUserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (AdminUserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class CaptchaAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'captcha', 'deadline_time')


admin.site.register(Captcha, CaptchaAdmin)
