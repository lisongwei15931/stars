# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from oscar.apps.customer import app
import safety.urls
import assets.urls
import receiving_address.urls
import user_info.urls
import stock.urls
import wishlists.urls
import trading_information.urls
import userpickup.urls
import finance.urls


class CustomerApplication(app.CustomerApplication):
    name = 'customer'


    def get_urls(self):
        urls = [
            # 我的关注
            url(r'^myfav/', include(wishlists.urls)),
            # 账户安全
            url(r'^safety/', include(safety.urls)),
            # 账户资产
            url(r'^assets/', include(assets.urls)),
            # 收货地址
            url(r'^receiving-address/', include(receiving_address.urls)),
            # 交易信息
            url(r'^trading-information/', include(trading_information.urls)),
            url(r'^stock/', include(stock.urls)),
            # 个人信息
            url(r'^user_info/', include(user_info.urls)),
            # 自提点
            url(r'^userpickup/', include(userpickup.urls)),
            # 签约支付
            url(r'^fin/', include(finance.urls)),
            ] + super(self.__class__, self).get_urls()

        return self.post_process_urls(urls)


application = CustomerApplication()
