# -*- coding: utf-8 -*-s

from django.contrib import admin
from django.contrib.auth.models import User

from stars.apps.api.models import App


class AppAdmin(admin.ModelAdmin):
    list_display = ('version', 'operaing_system', 'need_forced_update')


admin.site.register(App, AppAdmin)
