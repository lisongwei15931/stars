#coding=utf-8

from django.utils.translation import ugettext_lazy as _
from django_tables2 import Column, LinkColumn, TemplateColumn, A
from oscar.core.loading import get_class, get_model

DashboardTable = get_class('dashboard.tables', 'DashboardTable')
PickupStore = get_model('pickup_admin','PickupStore')
PickupDetail = get_model('commission','PickupDetail')
TradeComplete = get_model('commission','TradeComplete')
Product = get_model('catalogue','Product')


class ProductTable(DashboardTable):
    upc = Column(
        verbose_name=u'商品代码',
        order_by='upc')
    title = Column(
        verbose_name=u'商品名称',
        order_by='title')
    quote = Column(
        verbose_name=u'进货权',
        order_by='stock_config_product__quote')
    max_buy_num = Column(
        verbose_name=u'最大购买量',
        order_by='stock_config_product__max_buy_num')
    max_deal_num = Column(
        verbose_name=u'最大进货量',
        order_by='stock_config_product__max_deal_num')
    opening_price = Column(
        verbose_name=u'上市价格',
        order_by='stock_config_product__opening_price')
    once_max_num = Column(
        verbose_name=u'单笔最大下单量',
        order_by='stock_config_product__once_max_num')
    max_num = Column(
        verbose_name=u'用户持有总量',
        order_by='stock_config_product__max_num')
    pickup_price = Column(
        verbose_name=u'提货费用',
        order_by='stock_config_product__pickup_price')
    express_price = Column(
        verbose_name=u'快递费用',
        order_by='stock_config_product__express_price')
    sale_num = Column(
        verbose_name=u'发售量',
        order_by='stock_config_product__sale_num')
    up_up_range = Column(
        verbose_name=u'涨幅参数(%)',
        order_by='stock_config_product__up_up_range')
    up_down_range = Column(
        verbose_name=u'跌幅参数(%)',
        order_by='stock_config_product__up_down_range')
    min_bnum = Column(
        verbose_name=u'最小买申报单位',
        order_by='stock_config_product__min_bnum')
    min_snum = Column(
        verbose_name=u'最小卖申报单位',
        order_by='stock_config_product__min_snum')
    is_associate= TemplateColumn(
        verbose_name=u'关联状态',
        template_name='dashboard/business/product_row_is_associate.html',
        order_by='is_associate')
    trader = Column(
        verbose_name=u'关联交易员',
        order_by='trader')
    actions = TemplateColumn(
        verbose_name=u'动作',
        template_name='dashboard/business/product_row_action.html',
        orderable=False)
    caption = u'商品查询'

    class Meta(DashboardTable.Meta):
        model = Product
        fields = ('upc', 'title', 'is_associate', 'trader')
        sequence = ('upc', 'title', 'quote', 'max_buy_num', 'max_deal_num',
                    'opening_price', 'once_max_num', 'max_num', 'pickup_price',
                    'express_price', 'sale_num', 'up_up_range', 'up_down_range',
                    'min_bnum', 'min_snum', 'is_associate', 'trader')
        order_by = 'upc'


class StoreInCommApplyTable(DashboardTable):
    applyid = Column(verbose_name=_(u'发货单'),)
    # isp = Column(verbose_name=u'交易商')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/business/pickup_store_row_upc.html',
        order_by='product__upc')
    product = Column(
        verbose_name=_(u'商品名称'),
        )
    quantity = Column(
        verbose_name=_(u'发货数量'),
        #template_name='dashboard/catalogue/product_row_variants.html',
    )
    pickup_addr = Column(verbose_name=u'提货点')
    plan_income_date = Column(verbose_name = _(u'计划入库日期'))
    apply_date = Column(verbose_name = _(u'申请日期'))
    income_quantity = Column(verbose_name = _(u'入库数量'))
    lose_quantity = Column(verbose_name = _(u'丢失数量'))
    damaged_quantity = Column(verbose_name = _(u'损毁数量'))
    status = Column(verbose_name = _(u'审核状态'))

    actions = TemplateColumn(
        verbose_name='动作',
        template_name='dashboard/business/storeincomapply_action.html',
        orderable=False)

    icon = "sitemap"

    class Meta(DashboardTable.Meta):
        #model = StoreInComeApply
        #exclud = ('id',)
        sequence = ('applyid', 'upc', 'product', 'quantity',
                    'pickup_addr', 'plan_income_date', 'apply_date',
                    'income_quantity', 'lose_quantity', 'damaged_quantity',
                    'status', 'actions',)
        order_by = '-apply_date'


class Pickup_ApplyDashboard(DashboardTable):
    pickup_list_id = Column(verbose_name=u'提货单')
    product = Column(verbose_name=u'提货商品')
    quantity = Column(verbose_name=u'提货数量')
    unit_price= Column(verbose_name=u'商品单价')
    pickup_fee = Column(verbose_name=u'提货费用')
    pickup_type = Column(verbose_name=u'提货类型')
    status = Column(verbose_name=u'发货状态')
    created_date = Column(verbose_name=u'创建日期')

    icon = "sitemap"

    class Meta(DashboardTable.Meta):
        order_by = '-created_date'

class Product_QuotationDashboard(DashboardTable):
    product_symbol = Column(verbose_name=u'商品代码')
    product = Column(verbose_name=u'商品')
    strike_price = Column()
    net_change = Column()
    net_change_rise= Column()
    bid_price = Column()
    ask_price = Column()
    bid_vol = Column()
    ask_vol = Column()
    opening_price = Column()
    closing_price = Column()
    high = Column()
    low = Column()
    volume = Column()
    total = Column()
    market_capitalization = Column()
    created_date = Column()
    icon = "sitemap"

    class Meta(DashboardTable.Meta):
        order_by = '-created_date'

class BusinessPickupStoreTable(DashboardTable):
    pickup_addr = Column(
        verbose_name=u'提货点',
        order_by='pickup_addr__name')
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/business/pickup_store_row_upc.html',
        order_by='product__upc')
    caption = u'交易商自提点库存统计'
    icon = 'sitemap'

    class Meta(DashboardTable.Meta):
        model = PickupStore
        fields = ('quantity', 'locked_quantity')
        sequence = ('pickup_addr', 'product', 'upc', 'quantity', 'locked_quantity')
        order_by = 'pickup_addr'

class PickupOutStoreTable(DashboardTable):
    pickup_addr__name = Column(verbose_name=u'自提点',)
    product__title = Column(
        verbose_name=u'商品名称',
        order_by='product__title')
    product__upc = Column(
        verbose_name=u'商品代码',
        order_by='product__upc')
    pickup_type = TemplateColumn(
        verbose_name=u'提货类型',
        template_name='dashboard/business/pickup_store_row_pickuptype.html',
        accessor=A('pickup_type'),
        )
    status = TemplateColumn(verbose_name=u'提货状态',
                        template_name='dashboard/business/pickup_store_row_status.html')
    quantity = Column()
    count_quantity = TemplateColumn(verbose_name=u'商品总量',
                                    template_name='dashboard/business/business_product_row_quantity.html',
                                    orderable =False)
    lack_quantity = TemplateColumn(verbose_name=u'库存短缺',
                                   template_name='dashboard/business/pickup_store_row_lost.html',
                                   orderable=False)
    caption = u'出库查询'
    icon='sitemap'

    class Meta(DashboardTable.Meta):
        sequence = ('pickup_addr__name', 'product__title',
                    'product__upc', 'count_quantity','quantity', 'lack_quantity','pickup_type', 'status',
                )
        order_by = 'product__upc'

class BusinessProductTable(DashboardTable):
    #check = TemplateColumn(
    #    template_name='dashboard/users/user_row_checkbox.html',
    #    verbose_name=' ', orderable=False)
    #stockid = Column(verbose_name=u'入库单',)
    '''
    businessid = TemplateColumn(verbose_name=u'商家编号',
                                template_name='dashboard/business/business_user_row_uid.html',
                                orderable=False)
    business = TemplateColumn(verbose_name=u'商家名称',
                              template_name='dashboard/business/business_user_row_name.html',
                              order_by='user_id')
    stock_price = TemplateColumn(
                    verbose_name=u'上市价格',
                    template_name='dashboard/business/product_row_stockprice.html',
                    orderable=False
                    )
    '''
    upc = TemplateColumn(verbose_name=u'商品代码',
                         template_name='dashboard/business/pickup_store_row_upc.html',
                         order_by='product__upc')
    title = Column(verbose_name=u'商品名称',accessor=A('product'))
    number = Column(verbose_name=u'商品件数')
    quantity = Column(verbose_name=u'商品数量',)
    created_datetime = Column(verbose_name=u'申请时间')
    desc = Column(verbose_name=u'备注', orderable=False)
    status = Column(verbose_name=u'状态')
    deal_user = Column(verbose_name=u'审核人')
    deal_datetime = Column(verbose_name=u'审核时间')
    '''
    actions = TemplateColumn(
        verbose_name=' ',
        template_name='dashboard/business/business_product_edit.html',
        )
    '''

    caption = u'商品库转交易查询'
    icon='sitemap'

    class Meta(DashboardTable.Meta):
        #template='dashboard/business/stocktable.html'
        order_by = '-created_datetime'


class BusinessStockEnterDealTable(DashboardTable):
    #check = TemplateColumn(
    #    template_name='dashboard/users/user_row_checkbox.html',
    #    verbose_name=' ', orderable=False)
    stockid = Column(verbose_name=u'入库单号',)
    '''
    businessid = TemplateColumn(verbose_name=u'商家编号',
                                template_name='dashboard/business/business_user_row_uid.html',
                                orderable=False)
    business = TemplateColumn(verbose_name=u'商家名称',
                              template_name='dashboard/business/business_user_row_name.html',
                              order_by='user_id')
    stock_price = TemplateColumn(
                    verbose_name=u'上市价格',
                    template_name='dashboard/business/product_row_stockprice.html',
                    orderable=False
                    )
    '''
    upc = TemplateColumn(verbose_name=u'商品代码',
                         template_name='dashboard/business/pickup_store_row_upc.html',
                         order_by='product__upc')
    title = Column(verbose_name=u'商品名称',accessor=A('product'))
    user = Column(verbose_name=u'申请人')
    number = Column(verbose_name=u'商品件数')
    number = Column(verbose_name=u'商品件数')
    quantity = Column(verbose_name=u'商品数量',)
    created_datetime = Column(verbose_name=u'申请时间')
    desc = Column(verbose_name=u'备注', orderable=False)
    status = Column(verbose_name=u'状态')
    deal_user = Column(verbose_name=u'审核人')
    deal_datetime = Column(verbose_name=u'审核时间')
    actions = TemplateColumn(
        verbose_name=u'动作',
        template_name='dashboard/business/business_stockenter_actions.html',
        )

    caption = u'商品库转交易查询'
    icon='sitemap'

    class Meta(DashboardTable.Meta):
        #template='dashboard/business/stocktable.html'
        order_by = '-created_datetime'


class BusinessSaleTable(DashboardTable):
    isp = TemplateColumn(verbose_name = u'用户',
                         template_name='dashboard/business/business_sale_row_isp.html',
                         )
    ispname = TemplateColumn(verbose_name = u'商家名称',
                         template_name='dashboard/business/business_sale_row_ispname.html',
                         )
    upc = TemplateColumn(
    verbose_name=u'商品代码',
    template_name='dashboard/business/pickup_store_row_upc.html',
        order_by='product__upc')
    created_date = Column(verbose_name=u'成交日期')
    can_pickup_quantity = Column(verbose_name=u'待提取量')
    yet_pickup_quantity = TemplateColumn(verbose_name=u'已提取量',
                                         template_name='dashboard/business/business_sale_row_yetpick.html',)

    caption = u'商品销售情况'
    icon = 'sitemap'
    class Meta(DashboardTable.Meta):
        model = TradeComplete
        fields=('product','c_type','unit_price','quantity','total','can_pickup_quantity','created_date')
        sequence=('isp','ispname','product','upc','c_type','unit_price','quantity','total','can_pickup_quantity','yet_pickup_quantity','created_date')

        order_by = '-created_date'

class BusinessProfitTable(DashboardTable):
    title = Column(verbose_name=u'商品')
    upc = Column(
    verbose_name=u'商品代码',
        order_by='upc')
    isp_user = Column(verbose_name=u'商家用户')
    isp = Column(
        verbose_name=u'商家名称',
        orderable=False
                        )
    quantity = Column(verbose_name=u'销售数量',)
    avgprice =Column(verbose_name=u'销售均价')
    sales = Column(verbose_name=u'销售额',)
    profit = Column(verbose_name=u'商品利润',)
    created_date = Column(verbose_name=u'截止时间')
    caption = u'商品交易日销售额/利润'
    icon = 'sitemap'
    class Meta(DashboardTable.Meta):
        sequence=('isp_user','isp','title','upc','quantity','avgprice','sales','profit','created_date')
        order_by = '-created_date'


class BusinessBalanceTable(DashboardTable):
    isp_user = Column(verbose_name=u'商家用户')
    isp = Column(verbose_name=u'商家名称')
    sales = Column(verbose_name=u'销售额')
    profit = Column(verbose_name=u'利润')
    balance = Column(verbose_name=u'余额')
    can_pickup_balance = Column(verbose_name=u'可提金额')

    caption=u'商家账户资金'
    icon = 'sitemap'

    class Meta(DashboardTable.Meta):
        order_by = 'isp'

class ExpressSendTable(DashboardTable):
    pickup_list_id = Column(verbose_name=u'发货单',order_by='pickup_list_id')
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    quantity = Column(verbose_name=u'发货数量')
    consignee = Column(verbose_name=u'收货人')
    user_address = Column(verbose_name=u'收货地址')
    mobile_phone = Column(verbose_name=u'联系电话')
    status = Column(verbose_name=u'状态')
    logistics_company = Column(verbose_name=u'物流公司')
    logistics_no = Column(verbose_name=u'物流单号')
    refuse_desc = Column(verbose_name=u'驳回原因')
    deal_datetime = Column(verbose_name=u'办理时间')
    actions = TemplateColumn(
        verbose_name=u'动作',
        template_name='dashboard/business/express_send_deal_action.html',
        orderable=False)
    caption = u'发货信息'
    icon = 'sitemap'
    
    class Meta(DashboardTable.Meta):
        sequence=('pickup_list_id','upc','product','quantity','consignee','user_address',
                  'mobile_phone','status','logistics_company','logistics_no','refuse_desc','deal_datetime','actions')
        order_by = '-pickup_list_id'
        
class TraderProductTable(DashboardTable):
    upc = Column(
        verbose_name=u'商品代码',
        order_by='upc')
    title = Column(
        verbose_name=u'商品名称',
        order_by='title')
    quote = Column(
        verbose_name=u'进货权',
        order_by='stock_config_product__quote')
    max_buy_num = Column(
        verbose_name=u'最大购买量',
        order_by='stock_config_product__max_buy_num')
    max_deal_num = Column(
        verbose_name=u'最大进货量',
        order_by='stock_config_product__max_deal_num')
    opening_price = Column(
        verbose_name=u'上市价格',
        order_by='stock_config_product__opening_price')
    once_max_num = Column(
        verbose_name=u'单笔最大下单量',
        order_by='stock_config_product__once_max_num')
    max_num = Column(
        verbose_name=u'用户持有总量',
        order_by='stock_config_product__max_num')
    pickup_price = Column(
        verbose_name=u'提货费用',
        order_by='stock_config_product__pickup_price')
    express_price = Column(
        verbose_name=u'快递费用',
        order_by='stock_config_product__express_price')
    sale_num = Column(
        verbose_name=u'发售量',
        order_by='stock_config_product__sale_num')
    up_up_range = Column(
        verbose_name=u'涨幅参数(%)',
        order_by='stock_config_product__up_up_range')
    up_down_range = Column(
        verbose_name=u'跌幅参数(%)',
        order_by='stock_config_product__up_down_range')
    min_bnum = Column(
        verbose_name=u'最小买申报单位',
        order_by='stock_config_product__min_bnum')
    min_snum = Column(
        verbose_name=u'最小卖申报单位',
        order_by='stock_config_product__min_snum')
    bcomm = Column(
        verbose_name=u'买手续费参数(%)',
        order_by='bcomm')
    scomm = Column(
        verbose_name=u'卖手续费参数(%)',
        order_by='scomm')
    caption = u'交易员关联商品'

    class Meta(DashboardTable.Meta):
        sequence = ('upc', 'title', 'quote', 'max_buy_num', 'max_deal_num',
                    'opening_price', 'once_max_num', 'max_num', 'pickup_price',
                    'express_price', 'sale_num', 'up_up_range', 'up_down_range',
                    'min_bnum', 'min_snum', 'bcomm', 'scomm')
        order_by = 'upc'