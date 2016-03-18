#!/usr/bin/env python
# encoding: utf-8


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from oscar.core.application import Application
from oscar.core.loading import get_class
from oscar.apps.basket.app import BasketApplication as CoreBasketApplication

from stars.apps.basket.views import (delete_line_view, clean_basket_view,
        order_settlement_view, basket_success_view, basket_error_view, line_quantity_set,
        line_buy_price_set, MoveToMyfavView, order_confirm, pay_order, order_cancel)

class BasketApplication(CoreBasketApplication):
    buy_view = get_class('basket.views', 'BuyView')
    def get_urls(self):
        urls = [
            url(r'^$', login_required()(self.summary_view.as_view()), name='summary'),
            url(r'^line-quantity-set/$', line_quantity_set, name='line_quantity_set'),
            url(r'^line-buy-price-set/$', line_buy_price_set, name='line_buy_price_set'),
            url(r'^delete-line/(?P<pk>\d+)/$', delete_line_view, name='delete_line'),
            url(r'^clean-basket/$', clean_basket_view, name='clean_basket'),
            url(r'^order-settlement/$', order_settlement_view, name='order_settlement'),
            url(r'^basket-success/$', basket_success_view, name='basket_success_view'),
            url(r'^basket-error/$', basket_error_view, name='basket_error_view'),
            url(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            url(r'^buy/(?P<pk>\d+)/$', self.buy_view.as_view(), name='buy'),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(),
                name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$',
                self.remove_voucher_view.as_view(), name='vouchers-remove'),
            url(r'^saved/$', login_required(self.saved_view.as_view()),
                name='saved'),

            # 从购物车移动到我的关注
            url(r'^move-to-myfav/(?P<pk>\d+)/$', login_required(MoveToMyfavView.as_view()),
                name='move_to_myfav'),
            # 确认订单
            url(r'^order-confirm/$', login_required(order_confirm),
                name='order_confirm'),
            url(r'^pay-order/(?P<pk>\d+)/$', login_required(pay_order),
                name='pay_order'),
            url(r'^order-cancel/(?P<pk>\d+)/$', login_required(order_cancel),
                name='order_cancel'),
        ]
        return self.post_process_urls(urls)


application = BasketApplication()
