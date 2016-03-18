# coding=utf-8
from django.conf.urls import patterns, url, include
from rest_framework.authentication import BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

import finance.urls
import wishlists.urls
from stars.apps.api.address.views import AddressListView, AddressView, PickupAddressListView, PickupAddressView, \
    AddressAllView, RegionListView
from stars.apps.api.assets.views import AssetsSummaryView, AssetsIncomeListView
from stars.apps.api.product.views import CategoryProductListView, ProductSearchView
from stars.apps.api.userinfo.views import UserBaseInfoView
from stars.apps.api.views import (APIRechargeView, APIBuyView, APISellView,
    APIFactorySellView, APIProductStockView, APIProductIdsView, APIUserProductView,
    APIPickupView, APIRegisterView, APIGetappversionView,APIGetsmscodeView,
    APITestTokenView, APILoginView, APIGetimgverifycodeView, APIFindpwdView,
    APIResetpwdView, APIUpdateavatarView, APICheckusernameView, APIUpdateusernameView,
    APIGetmaininfolistView, APIGetmoreproductlistView, APIGetcategoryView,
    APIGetproductdetailView, APIAddtobasketView, APIGetBasketView, APIDelCartProductView,
                                  APIGetprobyattrView, APIUpdateCartNumView, APITradeInView,
    APITradeOutView, APICommitCartView, APIGetOrdersView, APIGetOrderDetailView, APICommitOrderView,
    APICancelOrderView, APIGetMyselfView, APIBatchQueryView, APIBatchAddtobasketView)

urlpatterns = patterns('',
    url(r'^auth/', 'rest_framework_jwt.views.obtain_jwt_token', name='api_auth'),
)

urlpatterns += patterns('stars.apps.api.views',
    url(r'^recharge/$', APIRechargeView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_recharge'),
    url(r'^buy/$', APIBuyView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_buy'),
    url(r'^sell/$', APISellView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_sell'),
    url(r'^factory/sell/$', APIFactorySellView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_sell'),
    url(r'^product/stock/$', APIProductStockView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_product_stock'),
    url(r'^product/ids/$', APIProductIdsView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_product_ids'),
    url(r'^user/product/$', APIUserProductView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_user_product'),
    url(r'^pickup/$', APIPickupView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_pickup'),
    url(r'^test/$', APITestTokenView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='test'),
    # about account
    url(r'^getappversion/$', APIGetappversionView.as_view(authentication_classes=[BasicAuthentication]), name='api_getappversion'),
    url(r'^getsmscode/$', APIGetsmscodeView.as_view(authentication_classes=[BasicAuthentication]), name='api_getsmscode'),
    url(r'^getimgverifycode/$', APIGetimgverifycodeView.as_view(authentication_classes=[BasicAuthentication]), name='api_getimgverifycode'),
    url(r'^findpwd/$', APIFindpwdView.as_view(authentication_classes=[BasicAuthentication]), name='api_findpwd'),
    url(r'^resetpwd/$', APIResetpwdView.as_view(authentication_classes=[BasicAuthentication]), name='api_resetpwd'),
    url(r'^updateavatar/$', APIUpdateavatarView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_updateavatar'),
    url(r'^checkusername/$', APICheckusernameView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_checkusername'),
    url(r'^updateusername/$', APIUpdateusernameView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_updateusername'),
    url(r'^register/$', APIRegisterView.as_view(authentication_classes=[BasicAuthentication]), name='api_register'),
    url(r'^login/$', APILoginView.as_view(authentication_classes=[BasicAuthentication]), name='api_login'),

    # 用户信息
    url(r'^userinfo/$', UserBaseInfoView.as_view(), name='api_userinfo'),
    # about home page
    url(r'^getmaininfolist/$', APIGetmaininfolistView.as_view(authentication_classes=[BasicAuthentication]), name='api_getmaininfolist'),
    url(r'^getmoreproductlist/$', APIGetmoreproductlistView.as_view(authentication_classes=[BasicAuthentication]), name='api_getmoreproductlist'),
    url(r'^getcategory/$', APIGetcategoryView.as_view(authentication_classes=[BasicAuthentication]), name='api_getcategory'),
    url(r'^getproductdetail/(?P<product_id>\d+)/$', APIGetproductdetailView.as_view(), name='api_getcategory'),
    url(r'^getprobyattr/(?P<product_id>\d+)/$', APIGetprobyattrView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_getprobyattr'),
    # basket
    url(r'^addtobasket/(?P<product_id>\d+)/$', APIAddtobasketView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_addtobasket'),
    url(r'^batchaddtobasket/$', APIBatchAddtobasketView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_batchaddtobasket'),

    url(r'^category/products/(?P<category_id>\d+)/$', CategoryProductListView.as_view(), name='api_category-products'),
    url(r'^product/search/$', ProductSearchView.as_view(), name='api_product-search'),
    url(r'^assets/summary/$', AssetsSummaryView.as_view(), name='api_assets-summary'),
    url(r'^assets/income/list/(?P<flag>(locked)|(details))/$', AssetsIncomeListView.as_view(), name='api_assets-income-list'),
    # 地址
    url(r'^address/pickup/user/list/$', PickupAddressListView.as_view(), name='api_pickup_address-list'),
    # url(r'^address/pickup/add/$', PickupAddressView.as_view(), name='api_pickup_address-add'),
    url(r'^address/pickup/user/(?P<address_id>\d+)/$', PickupAddressView.as_view(), name='api_pickup_address'),

    url(r'^address/all/$', AddressAllView.as_view(), name='api_address-all'),
    url(r'^address/list/$', AddressListView.as_view(), name='api_address-list'),
    url(r'^address/add/$', AddressView.as_view(), name='api_address-add'),
    url(r'^address/(?P<address_id>\d+)/$', AddressView.as_view(), name='api_address'),

    url(r'^region/list/$', RegionListView.as_view(), name='api_region-list'),

    # 资产
    url(r'^fin/', include(finance.urls)),

    # 我的关注
    url(r'^myfav/', include(wishlists.urls)),


    url(r'^getbasket/$', APIGetBasketView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_getbasket'),
    url(r'^batchquery/$', APIBatchQueryView.as_view(authentication_classes=[BasicAuthentication]), name='api_batchquery'),
    url(r'^delcartproduct/$', APIDelCartProductView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_delcartproduct'),
    url(r'^updatecartnum/$', APIUpdateCartNumView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_updatecartnum'),
    url(r'^tradein/$', APITradeInView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_tradein'),
    url(r'^tradeout/$', APITradeOutView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_tradeout'),
    
    url(r'^commitcart/$', APICommitCartView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_commitcart'),
    url(r'^commitorder/$', APICommitOrderView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_commitorder'),
    url(r'^getorderdetail/(?P<order_id>\d+)/$', APIGetOrderDetailView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_getorderdetail'),
    url(r'^cancelorder/(?P<order_id>\d+)/$', APICancelOrderView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_cancelorder'),
    url(r'^getorders/$', APIGetOrdersView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_getorders'),
    url(r'^product_description/(?P<pid>\d+)/$', 'product_description', name='product_description'),
    # 我的
    url(r'^getmyself/$', APIGetMyselfView.as_view(authentication_classes=[JSONWebTokenAuthentication]), name='api_getmyself'),
)
