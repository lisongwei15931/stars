from oscar.apps.address.admin import *  # noqa

from stars.apps.address.models import (Province, City, District,
                                       ReceivingAddress)


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug_name')
    search_fields = ('name', 'slug_name')


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug_name', 'province', 'lng', 'lat')
    search_fields = ('name', 'slug_name', 'province')


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug_name', 'city')
    search_fields = ('name', 'slug_name', 'city')


class ReceivingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'consignee', 'province', 'city', 'district',
                    'address', 'mobile_phone', 'telephone', 'is_default')
    search_fields = ('user', 'consignee', 'city')


admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(ReceivingAddress, ReceivingAddressAdmin)
admin.site.unregister(get_model('address', 'useraddress'))
