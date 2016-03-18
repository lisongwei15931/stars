
from django.contrib import admin

from stars.apps.commission.models import (CommissionBuy,CommissionSale,StockTicker,UserPickupCity,
                                          TradeComplete,CommissionBuyBackup,CommissionSaleBackup,
                                          PickupAddr,UserPickupAddr,StockProductConfig,
                                          UserMoneyChange,UserBalance,UserBank, PickupList,
                                          PickupDetail,SystemConfig,UserProduct,UserAssetDailyReport,ConfirmDeal,ProductOrder,
                                          OrderInfo)

class CommissionBuyAdmin(admin.ModelAdmin):
    readonly_fields = ('created_datetime','modified_datetime')
    list_display = ('user','product','c_type','created_datetime')


class CommissionBuyBackupAdmin(admin.ModelAdmin):
    readonly_fields = ('created_datetime','modified_datetime')
    list_display = ('user','product','c_type','created_datetime')


class CommissionSaleAdmin(admin.ModelAdmin):
    readonly_fields = ('created_datetime','modified_datetime')
    list_display = ('user','product','c_type','created_datetime')


class CommissionSaleBackupAdmin(admin.ModelAdmin):
    readonly_fields = ('created_datetime','modified_datetime')
    list_display = ('user','product','c_type','created_datetime')


class TradeCompleteAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date','created_datetime','modified_datetime')
    list_display = ('product', 'commission_buy_user_id',
                    'commission_sale_user_id', 'c_type', 'unit_price',
                    'quantity', 'can_pickup_quantity', 'total', 'created_datetime')


class StockTickerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date','created_datetime','modified_datetime')
    list_display = ('product','created_date')

class UserProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'trade_type', 'quantity', 'can_pickup_quantity',
                    'overage_unit_price', 'quote_quantity', 'total_buy_quantity',
                    'total_sale_quantity','total_pickup_quantity')


class PickupAddrAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'province', 'city', 'district',
                    'addr', 'lng', 'lat')
    filter_horizontal = ('staff',)


class UserPickupAddrAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pickup_addr', 'is_default')


class PickupListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pickup_no', 'pickup_type', 'status',
                    'pickup_fee', 'express_fee')


class PickupDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickup_list_id', 'pickup_type', 'status',
                    'pickup_fee', 'express_fee', 'pickup_addr', 'pickup_captcha')


class StockProductConfigAdmin(admin.ModelAdmin):
    list_display = ('product', 'pickup_price', 'express_price',)
    filter_horizontal = ('pickup_addr','distribution_pickup_addr',)


class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'locked', 'desc')


class UserMoneyChangeAdmin(admin.ModelAdmin):
    list_display = ('user', 'trade_type', 'price', 'product','created_date')


class UserAssetDailyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_date','start_balance','income','locked','total')


class UserPickupCityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    filter_horizontal = ('city',)


class ConfirmDealAdmin(admin.ModelAdmin):
    list_display = ('commission_buy_id', 'commission_sale_id')
    
    
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user','amount','description','detail')
    

class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ('product_order','product','product_num','price')

admin.site.register(CommissionBuy,CommissionBuyAdmin)
admin.site.register(CommissionSale,CommissionSaleAdmin)
admin.site.register(StockTicker,StockTickerAdmin)
admin.site.register(TradeComplete,TradeCompleteAdmin)
admin.site.register(CommissionBuyBackup,CommissionBuyBackupAdmin)
admin.site.register(CommissionSaleBackup,CommissionSaleBackupAdmin)
admin.site.register(PickupAddr, PickupAddrAdmin)
admin.site.register(PickupList, PickupListAdmin)
admin.site.register(UserPickupAddr, UserPickupAddrAdmin)
admin.site.register(StockProductConfig, StockProductConfigAdmin)
admin.site.register(UserMoneyChange, UserMoneyChangeAdmin)
admin.site.register(UserBalance, UserBalanceAdmin)
admin.site.register(UserBank)
admin.site.register(PickupDetail, PickupDetailAdmin)
admin.site.register(SystemConfig)
admin.site.register(UserPickupCity, UserPickupCityAdmin)
admin.site.register(UserProduct, UserProductAdmin)
admin.site.register(UserAssetDailyReport, UserAssetDailyReportAdmin)
admin.site.register(ConfirmDeal, ConfirmDealAdmin)
admin.site.register(ProductOrder, ProductOrderAdmin)
admin.site.register(OrderInfo, OrderInfoAdmin)
