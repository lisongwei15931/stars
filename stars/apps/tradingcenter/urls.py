from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required



urlpatterns = patterns('stars.apps.tradingcenter.views',
    url(r'^$', 'trading_center_index', name='trading_center_index'),
    url(r'^trading-center-data/$', 'trading_center_data', name='trading_center_data'),
    url(r'^trading-center-buy-right-data/$', 'trading_center_buy_right_data', name='trading_center_buy_right_data'),
    url(r'^trading-center-sale-right-data/$', 'trading_center_sale_right_data', name='trading_center_sale_right_data'),
    url(r'^trading-center-new-product-data/$', 'trading_center_new_product_data', name='trading_center_new_product_data'),
    url(r'^trading-center-self-pick-data/$', 'trading_center_self_pick_data', name='trading_center_self_pick_data'),
    url(r'^receive-data$', 'receive_data', name='receive_data'),
    url(r'^truncate-database/$', 'truncate_database', name='truncate_database'),
    url(r'^add-self-pick/$', 'add_self_pick', name='add_self_pick'),
    url(r'^remove-self-pick/$', 'remove_self_pick', name='remove_self_pick'),
    url(r'^get-selected-products-info/$', 'get_selected_products_info', name='get_selected_products_info'),
    url(r'^multiple-deal/$', 'multiple_deal', name='multiple_deal'),
    url(r'^redirect-to-buy/(?P<pid>\d+)/$', 'redirect_to_buy', name='redirect_to_buy'),
    url(r'^market-closed/$', 'market_closed', name='market_closed'),
)
