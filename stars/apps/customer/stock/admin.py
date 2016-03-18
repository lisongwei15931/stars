# -*- coding: utf-8 -*-s

from django.contrib import admin

from stars.apps.customer.stock.models import PickupProvisionalRecord


class PickupProvisionalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'max_quantity', 'pickup_type', 'available')


admin.site.register(PickupProvisionalRecord, PickupProvisionalRecordAdmin)
