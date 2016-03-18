from django.contrib import admin

from stars.apps.dashboard.staticpages.models import FlatPageNew 

class FlatPageNewAdmin(admin.ModelAdmin):
    readonly_fields = ('created_datetime','modified_datetime')
    list_display = ('id','title','category','url','created_datetime')

admin.site.register(FlatPageNew, FlatPageNewAdmin)