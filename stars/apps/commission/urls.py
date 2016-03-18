# encoding: utf-8


from django.conf.urls import patterns, url

urlpatterns = patterns('stars.apps.commission.views',
    url(r'^commission-buy/$', 'commission_buy', name='commission_buy'),
    url(r'^commission-sale/$', 'commission_sale', name='commission_sale'),
    url(r'^commission-buy-test/$', 'commission_buy_test', name='commission_buy_test'),
    url(r'^commission-sale-test/$', 'commission_sale_test', name='commission_sale_test'),
    url(r'^factory-commission-sale/$', 'factory_commission_sale', name='factory_commission_sale'),
)
