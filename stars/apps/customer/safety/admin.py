# -*- coding: utf-8 -*-s

from django.contrib import admin

from stars.apps.customer.safety.models import MailVerificationCode, SmsVerificationCode


class MailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'type', 'status', 'data', 'comment', 'created_time', 'expired_time', 'modified_time')
    list_editable = ('status', )

class SmsVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'type', 'status', 'data', 'comment', 'created_time', 'expired_time', 'modified_time')
    list_editable = ('status', )


admin.site.register(MailVerificationCode, MailVerificationCodeAdmin)
admin.site.register(SmsVerificationCode, SmsVerificationCodeAdmin)
