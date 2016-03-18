#coding=utf-8
from oscar.apps.catalogue.admin import *  # noqa
from .models import SearchFilter,ProductAttribute,ProductGroup

admin.site.unregister(ProductAttribute,)

class SearchFilterUserMoneyChangeAdmin(admin.ModelAdmin):
    list_display = ('class_id','attribute', 'search_value', 'search_order', 'chose')
    
    
    def class_id(self,obj):
        return obj.attribute.product_class.name
    class_id.short_description= u'商品类'
    
    #过滤搜索属性
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'attribute':
            kwargs['queryset'] = ProductAttribute.objects.filter(search_filter=True)

        return super(SearchFilterUserMoneyChangeAdmin,self).formfield_for_foreignkey(db_field, request=request, **kwargs)

class SearchFilterInline(admin.TabularInline):
    model =  SearchFilter
    
class ProductAttributeAdmin(ProductAttributeAdmin):
    list_display = ('name', 'code', 'product_class', 'type')
    prepopulated_fields = {"code": ("name", )}
    inlines=[SearchFilterInline,]
    
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('attr',)
    

admin.site.register(SearchFilter,SearchFilterUserMoneyChangeAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductGroup, ProductGroupAdmin)
