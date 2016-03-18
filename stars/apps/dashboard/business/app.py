#coding=utf-8

from django.conf.urls import url
from oscar.core.application import Application
from oscar.core.loading import get_class
from stars.apps.accounts.decorators import permission_required
from .views import get_pickupaddr

class businessDashboardApplication(Application):
    name = None
    #default_permissions = ['is_staff', ]
    ProductListView = get_class('dashboard.business.views','ProductListView')
    ProductTraderUpdateView = get_class('dashboard.business.views','ProductTraderUpdateView')
    StroeInComeListView = get_class('dashboard.business.views','StroeInComeListView')
    StroeInComeCreateView =  get_class('dashboard.business.views','StroeInComeCreateView')
    StroeInComeUpdateView = get_class('dashboard.business.views','StroeInComeUpdateView')
    StroeInComeDeleteView = get_class('dashboard.business.views','StroeInComeDeleteView')
    Pickup_ApplyListView = get_class('dashboard.business.views','Pickup_ApplyListView')
    Product_QuotationListView = get_class('dashboard.business.views','Product_QuotationListView')
    BusinessPickupStoreListView = get_class('dashboard.business.views','BusinessPickupStoreListView')
    PickupOutStoreListView = get_class('dashboard.business.views','PickupOutStoreListView')
    BusinessProductListView = get_class('dashboard.business.views','BusinessProductListView')
    BusinessProductCreateView = get_class('dashboard.business.views','BusinessProductCreateView')
    BusinessProductUpdateView = get_class('dashboard.business.views','BusinessProductUpdateView')
    BusinessProductDeleteView = get_class('dashboard.business.views','BusinessProductDeleteView')
    BusinessSaleListView = get_class('dashboard.business.views','BusinessSaleListView')
    BusinessProfitListView = get_class('dashboard.business.views','BusinessProfitListView')
    BusinessBalanceListView = get_class('dashboard.business.views','BusinessBalanceListView')
    BusinessStockEnterDealListView = get_class('dashboard.business.views','BusinessStockEnterDealListView')
    BusinessStockEnterDealView = get_class('dashboard.business.views','BusinessStockEnterDealView')
    StoreIncomeDealView = get_class('dashboard.business.views','StoreIncomeDealView')
    BusinessLoginView = get_class('dashboard.business.views','BusinessLoginView')
    TraderLoginView = get_class('dashboard.business.views', 'TraderLoginView')
    PartnerUserListView = get_class('dashboard.business.views','PartnerUserListView')
    ExpressSendListView = get_class('dashboard.business.views','ExpressSendListView')
    ExpressSendDealView = get_class('dashboard.business.views','ExpressSendDealView')
    TraderProductListView = get_class('dashboard.business.views','TraderProductListView')
    TraderSaleListView = get_class('dashboard.business.views','TraderSaleListView')
    def get_urls(self):
        urls = [
                url(r'^product/list/$', permission_required(['dashboard_admin','member_unit'])(self.ProductListView.as_view()), name='business-product-list'),
                url(r'^product/update/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.ProductTraderUpdateView.as_view()), name='product-trader-update'),
                url(r'^storeincome/list/$', permission_required(['dashboard_admin','member_unit'])(self.StroeInComeListView.as_view()), name='storeincome-list'),
                url(r'^storeincome/update/$', permission_required(['dashboard_admin','member_unit'])(self.StroeInComeCreateView.as_view()), name='storeincomeapply-update'),
                url(r'^storeincome/update/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.StroeInComeUpdateView.as_view()), name='storeincomeapply-update-pk'),
                url(r'^storeincome/delete/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.StroeInComeDeleteView.as_view()), name='storeincomeapply-delete'),
                url(r'^pickup_apply/list/$', permission_required(['dashboard_admin','member_unit'])(self.Pickup_ApplyListView.as_view()), name='pickup-apply-list'),
                url(r'^product_quotation/list/$', permission_required(['dashboard_admin','member_unit'])(self.Product_QuotationListView.as_view()), name='product-quotation-list'),
                url(r'^business_pickupaddr/list/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessPickupStoreListView.as_view()), name='business-pickupaddr-list'),
                url(r'^pickup_outstore/list/$', permission_required(['dashboard_admin','member_unit'])(self.PickupOutStoreListView.as_view()), name='pickup-outstore-list'),
                url(r'^business_product/list/$', permission_required(['dashboard_admin','trader'])(self.BusinessProductListView.as_view()), name='business-product-store-list'),
                url(r'^business_product/create/$', permission_required(['dashboard_admin','trader'])(self.BusinessProductCreateView.as_view()), name='businessproduct-create'),
                url(r'^business_product/update/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessProductUpdateView.as_view()), name='businessproduct-update-pk'),
                url(r'^business_product/delete/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessProductDeleteView.as_view()), name='businessproduct-delete'),
                url(r'^business_sale/list/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessSaleListView.as_view()), name='business-sale-list'),
                url(r'^business_profit/list/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessProfitListView.as_view()), name='business-profit-list'),
                url(r'^business_balance/list/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessBalanceListView.as_view()), name='business-balance-list'),
                # deal stockenter
                url(r'^business_stockenter/list/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessStockEnterDealListView.as_view()), name='business-stockenter-deal-list'),
                url(r'^business_stockenter/deal/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.BusinessStockEnterDealView.as_view()), name='business-stockenter-deal'),
                url(r'^business_storeincome/deal/(?P<pk>\d+)/$', permission_required(['dashboard_admin','member_unit'])(self.StoreIncomeDealView.as_view()), name='business-storeincome-deal'),
                url(r'^business_login/$',self.BusinessLoginView.as_view(),name='business-login'),
                url(r'^trader_login/$',self.TraderLoginView.as_view(),name='trader-login'),
                # 会员单位
                url(r'^partner/list/$', permission_required(['dashboard_admin','member_unit'])(self.PartnerUserListView.as_view()), name='partneruser-list'),
                # 会员单位发货
                url(r'^express_send/list/$', permission_required(['dashboard_admin','member_unit'])(self.ExpressSendListView.as_view()), name='express-send-list'),
                url(r'^express_send/(?P<pk>\d+)/update/$', permission_required(['dashboard_admin','member_unit'])(self.ExpressSendDealView.as_view()), name='express-send-deal'),
                # 交易员
                url(r'^trader_product/list/$', permission_required(['dashboard_admin','trader'])(self.TraderProductListView.as_view()), name='trader-product-list'),
                url(r'^trader_sale/list/$', permission_required(['dashboard_admin','trader'])(self.TraderSaleListView.as_view()), name='trader-sale-list'),
                url(r'^get_pickupaddr/$',get_pickupaddr,name='get-pickupaddr'),

        ]
        return self.post_process_urls(urls)


application = businessDashboardApplication()
