# -*- coding: utf-8 -*-
from __future__ import division
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Sum, Case, When, Q, F, FloatField
from django.db.models.functions import Coalesce
from stars.apps.commission.models import TradeComplete, StockTicker
from stars.apps.customer.safety.common_const import Const


def mask_bank_card_no(no):
    if no:
        s = '*'*(len(no)-4) + no[-4:]
        r = s[:4] + ' '
        for i in range(1, (len(no)+3)//4):
            r += s[4*i:4*(i+1)] + ' '
        return r
    return no


def mask_id_card_no(id):

    return '{}***{}'.format(id[:9], id[-3:]) if id else ''


def is_valid_bank_card_num(num):
    r = num.replace(' ','')
    return 20 > len(r) > 10 and r.isdigit()


def is_valid_mobile(num):
    prefix=['130','131','132','133','134','135','136','137','138','139',
                 '150','151','152','153','156','158','159','170', '172',
                 '178','181', '182','183','185','186','187','188','189']

    return num and len(num) == 11 and num.isdigit() and num[0:3] in prefix


class _BankData(Const):
    BANK_IMG_URLS = {
                        # '中国工商银行': 'images/ABC.png',
                        u'中国农业银行': u'images/ABC.png',
                        # '中国银行': 'images/',
                        u'中国建设银行': u'images/CCB.png',
                        # '交通银行': 'images/',
                        # '中国邮政银行': 'images/',
                        u'招商银行': u'images/CMB.png',}
    BANK_CHOICES = set(BANK_IMG_URLS.keys())

BankData = _BankData()


def is_valid_bank(name):
    return name in BankData.BANK_CHOICES


class AssetsUtil():
    @staticmethod
    def get_profit_up_to_thd_day(user_id, the_date):
        """
        返回指定用户截至某天的累计收益
        :param user_id:
        :param the_date:截至此日期
        :return: 累计收益
        """
        # 截至昨天商品成本总价
        product_total_cost_price = TradeComplete.objects.filter(commission_buy_user_id_id=user_id,
                                                                c_type=2,
                                                                created_date__lte=the_date)\
        .aggregate(total=Coalesce(Sum('total'), 0.0))['total']

        # 截至昨天商品销售额
        sales_amount = TradeComplete.objects.filter(commission_sale_user_id_id=user_id, created_date__lte=the_date).aggregate(
            total=Coalesce(Sum('total'), 0.0))['total']

        # the_date前一天收盘时库存价格总额
        rs = TradeComplete.objects.filter((Q(commission_buy_user_id_id=user_id) & Q(c_type=2)) | Q(commission_sale_user_id_id=user_id),
                                          created_date__lte=the_date)\
            .values('product_id')\
            .annotate(product_num=Sum(Case(When(commission_buy_user_id_id=user_id,then='quantity'), default=0-F('quantity'))))\
            # .value_list('product_id', 'product_num')

        d = {ele['product_id']: ele['product_num'] for ele in rs if ele['product_num']!=0}

        stock_product_total_price = 0

        if d:
            sql = 'select a.id,a.product_id,a.closing_price from commission_stockticker as a ' \
                  'where a.product_id in %(ids)s and ' \
                    ' a.created_date = (select max(created_date) from commission_stockticker as b ' \
                                        'where b.product_id=a.product_id and b.created_date<=%(thd_day)s ) ' \
                  ' group by product_id'
            rs = StockTicker.objects.raw(sql, {'ids': d.keys(), 'thd_day': the_date + timedelta(days=1)})
            for ele in rs:
                stock_product_total_price += ele.closing_price * d[ele.product_id]

        # 累计收益
        return sales_amount + stock_product_total_price - product_total_cost_price

    @staticmethod
    def get_profit(user_id):
        """
        返回指定用户累计收益(截至昨天)、昨天收益
        :param user_id:
        :return: (累计收益, 昨天收益)
        """

        total_income_up_to_yesterday = AssetsUtil.get_profit_up_to_thd_day(user_id, datetime.today() - timedelta(days=1))
        total_income_up_to_the_day_before_yesterday = AssetsUtil.get_profit_up_to_thd_day(user_id, datetime.today() - timedelta(days=2))
        yesterday_income = total_income_up_to_yesterday - total_income_up_to_the_day_before_yesterday

        return total_income_up_to_yesterday, yesterday_income

    @staticmethod
    def get_product_avg_price(user_id, date):
        """
        计算指定用户在date当天库存每种商品的成本均价
        :param user_id:
        :param date:
        :return: 每种商品均价 {product_id: avg_price}
        """
        rs = TradeComplete.objects.filter(commission_buy_user_id_id=user_id, c_type=2, created_date__lte=date)\
            .values('product_id')\
            .annotate(avg_price=Coalesce(Sum('total',output_field=FloatField())/Sum('quantity',output_field=FloatField()), 0.0)
                      )
        r = defaultdict(float)
        for ele in rs:
            r[ele['product_id']] = ele['avg_price']

        return r
