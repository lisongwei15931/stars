#coding=utf-8

from django_tables2 import Table, A
from django_tables2.columns.base import Column
from django_tables2.columns import TemplateColumn
from oscar.core.loading import get_class, get_model

from stars.apps.commission.models import (CommissionBuy, TradeComplete,
                                          UserAssetDailyReport,)

DashboardTable = get_class('dashboard.tables', 'DashboardTable')

class CommissionQueryTable(DashboardTable):
    commission_no = Column(verbose_name=u'委托编号',
                    accessor=A('commission_no')
                    )
    isp = TemplateColumn(verbose_name=u'交易商',
          template_name='dashboard/dataquery/row_list/partner_row_list.html'
          )
    trader = Column(verbose_name=u'交易员',
             accessor='product.trader'
            )
    upc = Column(verbose_name=u'商品代码',accessor='product.upc')
    product = Column(verbose_name=u'商品')
    c_type = Column(verbose_name=u'交易类型')
    quantity = Column(verbose_name=u'数量')
    uncomplete_quantity = Column(verbose_name=u'未成交数量')
    status = Column(verbose_name=u'状态')
    created_datetime = Column(verbose_name=u'委托时间')
    unit_price = Column(verbose_name=u'委托价格')
    caption = u'委托查询'
    icon = "sitemap"
    class Meta(DashboardTable.Meta):
        #fields = ('product','c_type','unit_price','quantity','uncomplete_quantity','status','created_datetime')
        sequence = ('commission_no','isp','trader','upc',
                    'product','c_type','unit_price','quantity','uncomplete_quantity','status','created_datetime')
        

class TradeCompleteQueryTable(DashboardTable):
    trade_no = Column(verbose_name=u'成交编号',
                       accessor=A('trade_no'))
    isp = TemplateColumn(verbose_name=u'交易商',
                         template_name='dashboard/dataquery/row_list/partner_row_list.html'
          )
    trader = Column(verbose_name=u'交易员',
             accessor='product.trader'
            )
    upc = Column(verbose_name=u'商品代码',accessor='product.upc')
    charge = TemplateColumn(verbose_name=u'卖手续费',
                            template_name='dashboard/dataquery/row_list/trade_row_list.html'
                            )
    created_datetime = Column(verbose_name=u'成交时间')
    caption = u'成交查询'
    icon = "sitemap"
    class Meta(DashboardTable.Meta):
        model = TradeComplete
        fields = ('product','commission_buy_no','commission_sale_no','c_type','unit_price','quantity','total','created_datetime')
        sequence = ('trade_no','commission_buy_no','commission_sale_no','isp','trader','upc','product','c_type','unit_price','quantity','total','charge','created_datetime')
         

class HoldProductQueryTable(DashboardTable):
    isp = TemplateColumn(verbose_name=u'交易商',
                         template_name='dashboard/dataquery/row_list/partner_row_list2.html'
          )
    upc = TemplateColumn(verbose_name=u'商品代码',
                         template_name='dashboard/dataquery/row_list/upc_row_list.html'
                         )
    product = TemplateColumn(verbose_name=u'商品名称',
                             template_name='dashboard/dataquery/row_list/title_row_list.html'
              )
    today_buy = TemplateColumn(verbose_name=u'当天买量',
                               template_name='dashboard/dataquery/row_list/buy_row_list.html')
    today_sale = TemplateColumn(verbose_name=u'当天卖量',
                                template_name='dashboard/dataquery/row_list/sale_row_list.html')
    can_pickup = Column(verbose_name=u'可提货量')
    pickup = Column(verbose_name=u'提货量')
    quantity = Column(verbose_name=u'当前持有量')
    today_close = TemplateColumn(verbose_name=u'当前冻结量',
                                 template_name='dashboard/dataquery/row_list/tdclose_row_list.html')
    tn_close = TemplateColumn(verbose_name=u'T+N冻结量',
                              template_name='dashboard/dataquery/row_list/tnclose_row_list.html')
    unit_price = TemplateColumn(verbose_name=u'买入均价',
                                template_name='dashboard/dataquery/row_list/unitp_row_list.html')
    open_price = TemplateColumn(verbose_name=u'商品市值',
                                template_name='dashboard/dataquery/row_list/price_row_list.html')
    profit_loss = TemplateColumn(verbose_name=u'盈亏成本',
                                 template_name='dashboard/dataquery/row_list/profit_row_list.html')
    created_date = Column(verbose_name=u'当前日期')

    caption = u'持有查询'
    icon = "sitemap"
    class Meta(DashboardTable.Meta):
        sequence = ('isp', 'upc', 'product', 'today_buy', 'today_sale', 'can_pickup',
                    'pickup', 'quantity', 'today_close', 'tn_close', 'unit_price',
                    'open_price', 'profit_loss','created_date',
                    )

class StoreProductQueryTable(DashboardTable):
    isp = TemplateColumn(verbose_name=u'交易商',
                         template_name='dashboard/dataquery/row_list/partner_row_list2.html'
          )
    upc = TemplateColumn(verbose_name=u'商品代码',
                         template_name='dashboard/dataquery/row_list/upc_row_list.html'
                         )
    product = TemplateColumn(verbose_name=u'商品名称',
                             template_name='dashboard/dataquery/row_list/title_row_list.html'
              )
    today_buy = TemplateColumn(verbose_name=u'当天买量',
                               template_name='dashboard/dataquery/row_list/buy_row_list.html')
    today_sale = TemplateColumn(verbose_name=u'当天卖量',
                                template_name='dashboard/dataquery/row_list/sale_row_list.html')
    can_pickup = Column(verbose_name=u'可提货量')
    pickup = Column(verbose_name=u'提货量')
    quantity = Column(verbose_name=u'当前持有量')
    today_close = TemplateColumn(verbose_name=u'当前冻结量',
                                 template_name='dashboard/dataquery/row_list/tdclose_row_list.html')
    tn_close = TemplateColumn(verbose_name=u'T+N冻结量',
                              template_name='dashboard/dataquery/row_list/tnclose_row_list.html')
    unit_price = TemplateColumn(verbose_name=u'买入均价',
                                template_name='dashboard/dataquery/row_list/unitp_row_list.html')
    open_price = TemplateColumn(verbose_name=u'商品市值',
                                template_name='dashboard/dataquery/row_list/price_row_list.html')
    profit_loss = TemplateColumn(verbose_name=u'盈亏成本',
                                 template_name='dashboard/dataquery/row_list/profit_row_list.html')
    created_date = Column(verbose_name=u'当前日期')

    caption = u'存货查询'
    icon = "sitemap"
    class Meta(DashboardTable.Meta):
        sequence = ('isp', 'upc', 'product', 'today_buy', 'today_sale', 'can_pickup',
                    'pickup', 'quantity', 'today_close', 'tn_close', 'unit_price',
                    'open_price', 'profit_loss','created_date',
                    )



class StoreProductQueryAllTable(DashboardTable):
    isp = TemplateColumn(verbose_name=u'交易商',
                         template_name='dashboard/dataquery/row_list/partner_row_list2.html'
          )
    upc = TemplateColumn(verbose_name=u'商品代码',
                         template_name='dashboard/dataquery/row_list/upc_row_list.html'
                         )
    product = TemplateColumn(verbose_name=u'商品名称',
                             template_name='dashboard/dataquery/row_list/title_row_list.html'
              )
    buy = Column(verbose_name=u'买量')
    sale = Column(verbose_name=u'卖量')
    can_pickup = Column(verbose_name=u'可提货量')
    pickup = Column(verbose_name=u'提货量')
    quantity = Column(verbose_name=u'当前持有量')
    today_close = TemplateColumn(verbose_name=u'当前冻结量',
                                 template_name='dashboard/dataquery/row_list/tdclose_row_list.html')
    tn_close = TemplateColumn(verbose_name=u'T+N冻结量',
                              template_name='dashboard/dataquery/row_list/tnclose_row_list.html')
    unit_price = TemplateColumn(verbose_name=u'买入均价',
                                template_name='dashboard/dataquery/row_list/unitp_row_list.html')
    open_price = TemplateColumn(verbose_name=u'商品市值',
                                template_name='dashboard/dataquery/row_list/price_row_list.html')
    profit_loss = TemplateColumn(verbose_name=u'盈亏成本',
                                 template_name='dashboard/dataquery/row_list/profit_row_list.html')

    caption = u'存货查询'
    icon = "sitemap"
    class Meta(DashboardTable.Meta):
        sequence = ('isp', 'upc', 'product', 'buy', 'sale', 'can_pickup',
                    'pickup', 'quantity', 'today_close', 'tn_close', 'unit_price',
                    'open_price', 'profit_loss',
                    )

class CapitalQueryTable(DashboardTable):
    role = Column(verbose_name=u'用户角色', accessor=A('user.userprofile.role'))
    balance = Column(verbose_name=u'资金余额',accessor='can_use_amount')
    icon = "sitemap"

    class Meta(DashboardTable.Meta):
        model = UserAssetDailyReport
        fields = ('user','target_date', 'start_balance', 'income', 'expenditure',
                  'can_use_amount', 'can_out_amount', 'total')
        sequence = ('user', 'role', 'start_balance', 'income', 'expenditure',
                  'can_use_amount', 'can_out_amount', 'balance', 'total', 'target_date')
        order_by = ('-target_date','user')