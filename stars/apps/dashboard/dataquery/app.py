#coding=utf-8
from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.accounts.decorators import permission_required

class DataQueryApplication(Application):
    CommissionQueryListView = get_class('dashboard.dataquery.views', 'CommissionQueryListView')
    CommissionQueryAllListView = get_class('dashboard.dataquery.views', 'CommissionQueryAllListView')
    TradeCompleteQueryListView = get_class('dashboard.dataquery.views', 'TradeCompleteQueryListView')
    TradeCompleteQueryAllListView = get_class('dashboard.dataquery.views', 'TradeCompleteQueryAllListView')
    HoldProductListView = get_class('dashboard.dataquery.views', 'HoldProductListView')
    StoreProductListView = get_class('dashboard.dataquery.views', 'StoreProductListView')
    StoreProductAllListView = get_class('dashboard.dataquery.views','StoreProductAllListView')
    CapitalQueryListView = get_class('dashboard.dataquery.views','CapitalQueryListView')
    CapitalQueryAllListView = get_class('dashboard.dataquery.views','CapitalQueryAllListView')
    def get_urls(self):
        urls = [
                url(r'^commission-query-list/$',
                permission_required(['dashboard_admin',])(self.CommissionQueryListView.as_view()), name='commission-query-list'),
                url(r'^commission-query-all-list/$',
                permission_required(['dashboard_admin',])(self.CommissionQueryAllListView.as_view()), name='commission-query-all-list'),
                url(r'^tradecomplete-query-list/$',
                permission_required(['dashboard_admin',])(self.TradeCompleteQueryListView.as_view()), name='tradecomplete-query-list'),
                url(r'^tradecomplete-query-all-list/$',
                permission_required(['dashboard_admin',])(self.TradeCompleteQueryAllListView.as_view()), name='tradecomplete-query-all-list'),
                url(r'^hold-product-list/$',
                permission_required(['dashboard_admin',])(self.HoldProductListView.as_view()), name='hold-product-list'),
                url(r'^store-product-list/$',
                permission_required(['dashboard_admin',])(self.StoreProductListView.as_view()), name='store-product-list'),
                url(r'^store-product-all-list/$',
                permission_required(['dashboard_admin',])(self.StoreProductAllListView.as_view()), name='store-product-all-list'),
                url(r'^capital-query-list/$',
                permission_required(['dashboard_admin',])(self.CapitalQueryListView.as_view()), name='capital-query-list'),
                url(r'^capital-query-all-list/$',
                permission_required(['dashboard_admin',])(self.CapitalQueryAllListView.as_view()), name='capital-query-all-list'),

                ]
        return self.post_process_urls(urls)
    
    
    

application = DataQueryApplication()
    

