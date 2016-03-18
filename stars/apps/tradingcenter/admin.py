
from django.contrib import admin

from stars.apps.tradingcenter.models import SelfPick


class SelfPickAdmin(admin.ModelAdmin):
    filter_horizontal = ('product',)


admin.site.register(SelfPick, SelfPickAdmin)
