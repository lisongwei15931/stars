# -*- coding: utf-8 -*-s

from django.contrib import admin

from stars.apps.pickup_admin.models import (StoreInCome, PickupStore,
    StoreInComeApply, PickupStatistics)


class StoreInComeAdmin(admin.ModelAdmin):
    list_display = ('pickup_addr', 'isp', 'product', 'c_quantity', 'quantity',
                    'income_date', 'created_datetime', 'modified_datetime')


class PickupStoreAdmin(admin.ModelAdmin):
    list_display = ('pickup_addr', 'product', 'quantity', 'created_datetime',
                    'modified_datetime')


class StoreInComeApplyAdmin(admin.ModelAdmin):
    list_display = ('pickup_addr', 'isp', 'product', 'c_quantity', 'quantity',
                    'status', 'deal_datetime', 'deal_user', 'refuse_desc',
                    'created_datetime', 'modified_datetime')


class PickupStatisticsAdmin(admin.ModelAdmin):
    list_display = ('pickup_addr', 'product', 'quantity', 'pickup_type')


admin.site.register(StoreInCome, StoreInComeAdmin)
admin.site.register(PickupStore, PickupStoreAdmin)
admin.site.register(StoreInComeApply, StoreInComeApplyAdmin)
admin.site.register(PickupStatistics, PickupStatisticsAdmin)
