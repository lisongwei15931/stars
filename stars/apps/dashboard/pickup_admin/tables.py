# encoding: utf-8


from django_tables2.columns.templatecolumn import TemplateColumn
from django_tables2.tables import Table
from django_tables2.utils import A
from oscar.core.loading import get_class, get_model
from django_tables2.columns.base import Column


DashboardTable = get_class('dashboard.tables', 'DashboardTable')
PickupStore = get_model('pickup_admin', 'PickupStore')
StoreInComeApply = get_model('pickup_admin', 'StoreInComeApply')
StoreInCome = get_model('pickup_admin', 'StoreInCome')
PickupStatistics = get_model('pickup_admin', 'PickupStatistics')
PickupDetail = get_model('commission', 'PickupDetail')
PickupList = get_model('commission', 'PickupList')


class PickupDetailTable(DashboardTable):
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    pickup_type = Column(
        verbose_name=u'提货类型',
        accessor=A('pickup_type'),
        )
    caption = u'申请提货查询'

    class Meta(DashboardTable.Meta):
        model = PickupStore
        fields = ('pickup_list_id', 'pickup_captcha', 'pickup_addr', 'quantity',
                  'status', 'user_address', 'pickup_captcha', 'logistics_company',
                  'refuse_desc', 'deal_datetime', 'logistics_date', 'deal_user')
        sequence = ('pickup_list_id', 'pickup_captcha', 'pickup_addr', 'product',
                    'upc', 'quantity', 'pickup_type', 'status',
                    'user_address', 'logistics_company', 'refuse_desc',
                    'deal_datetime', 'logistics_date', 'deal_user')
        order_by = 'pickup_list_id'


class PickupDetailDealTable(DashboardTable):
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    actions = TemplateColumn(
        verbose_name=u'动作',
        template_name='dashboard/pickup_admin/pickup_detail_deal_action.html',
        orderable=False)
    caption = u'提货单'

    class Meta(DashboardTable.Meta):
        model = PickupStore
        fields = ('pickup_list_id', 'pickup_captcha', 'pickup_addr', 'quantity',
                  'status',
                  'refuse_desc', 'deal_datetime', 'logistics_date', 'deal_user')
        sequence = ('pickup_list_id', 'pickup_captcha', 'pickup_addr', 'product',
                    'upc', 'quantity', 'status',
                    'refuse_desc',
                    'deal_datetime', 'logistics_date', 'deal_user')
        order_by = '-pickup_list_id'


class PickupStoreTable(DashboardTable):
    pickup_addr = Column(
        verbose_name=u'提货点',
        order_by='pickup_addr__name')
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    caption = u'库存统计'

    class Meta(DashboardTable.Meta):
        model = PickupStore
        fields = ('quantity', 'locked_quantity')
        sequence = ('pickup_addr', 'product', 'upc', 'quantity', 'locked_quantity')
        order_by = 'pickup_addr'


class StoreInComeApplyTable(DashboardTable):
    pickup_addr = Column(
        verbose_name=u'提货点',
        orderable=False,
        order_by='pickup_addr__name')
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    telephone = Column(
        verbose_name=u'联系电话',
        orderable=False)
    actions = TemplateColumn(
        verbose_name=u'动作',
        template_name='dashboard/pickup_admin/store_income_apply_action.html',
        orderable=False)
    caption = u'入库办理'

    class Meta(DashboardTable.Meta):
        model = StoreInComeApply
        fields = ('quantity', 'damaged_quantity', 'lose_quantity', 'in_quantity',
                  'isp', 'plan_income_date', 'apply_date',
                  'status', 'deal_datetime', 'deal_user')
        sequence = ('pickup_addr', 'product', 'upc', 'isp', 'quantity', 'damaged_quantity',
                    'lose_quantity', 'in_quantity', 'plan_income_date', 'apply_date',
                    'telephone', 'status', 'deal_datetime', 'deal_user')
        order_by = '-status'


class StoreInComeTable(DashboardTable):
    pickup_addr = Column(
        verbose_name=u'提货点',
        orderable=False,
        order_by='pickup_addr__name')
    product = Column(
        verbose_name=u'商品名称',
        #template_name='dashboard/pickup_admin/store_income_row_product.html',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    caption = u'入库查询'

    class Meta(DashboardTable.Meta):
        model = StoreInCome
        fields = ('quantity', 'isp', 'place', 'les_space', 'income_date',
                  'product_company', 'place_of_origin', 'producttion_date',
                  'warehouse_rental_start_time', 'inspect_orig',
                  'inspect_cert', 'inspect_expert', 'vouch_company',)
        sequence = ('pickup_addr', 'product', 'upc', 'isp', 'quantity',
                    'product_company', 'place_of_origin', 'producttion_date',
                    'warehouse_rental_start_time', 'inspect_orig',
                    'inspect_cert', 'inspect_expert', 'vouch_company',
                    'place', 'les_space', 'income_date',)
        order_by = 'pickup_addr'


class PickupStatisticsTable(DashboardTable):
    pickup_addr = Column(
        verbose_name=u'提货点',
        orderable=False,
        order_by='pickup_addr__name')
    product = Column(
        verbose_name=u'商品名称',
        accessor=A('product'),
        order_by='product__title')
    upc = TemplateColumn(
        verbose_name=u'商品代码',
        template_name='dashboard/pickup_admin/pickup_store_row_upc.html',
        order_by='product__upc')
    caption = u'提货统计'

    class Meta(DashboardTable.Meta):
        model = StoreInCome
        fields = ('quantity', 'pickup_type')
        sequence = ('pickup_addr', 'product', 'upc', 'quantity', 'pickup_type')
        order_by = 'pickup_addr'
