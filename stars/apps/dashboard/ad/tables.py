# -*- coding: utf-8 -*-s

from django.utils.translation import ugettext_lazy as _
from django_tables2 import Column, LinkColumn, TemplateColumn, A, URLColumn

from oscar.core.loading import get_class, get_model
from stars.apps.ad.models import RollingAd

DashboardTable = get_class('dashboard.tables', 'DashboardTable')


class RollingAdTable(DashboardTable):
    title = LinkColumn('dashboard:ad-rolling_ad-update', args=[A('pk')])
    image = TemplateColumn(
        verbose_name=_('Image'),
        template_name='dashboard/ad/rolling_ad_row_image.html',
        orderable=False)
    link_url = URLColumn(
        verbose_name=_(u'链接地址'),
        accessor='link_url',
        orderable=False)
    description = TemplateColumn(
        verbose_name=_("Description"),
        accessor='description',
        orderable=False,

        template_code='{{ record.description|default:""|striptags'
                      '|cut:"&nbsp;"|truncatewords:6 }}')
    order_num = Column(
        verbose_name=_(u'顺序'),
        accessor='order_num',
        orderable=True)
    valid = Column(
        verbose_name=_(u'开启'),
        accessor='valid',
        orderable=False)
    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/ad/rolling_ad_row_actions.html', #'dashboard/ad/rolling_ad_row_actions.html',
        orderable=False)

    icon = "sitemap"

    class Meta(DashboardTable.Meta):
        model = RollingAd
        fields = ('title', 'position', 'image','link_url', 'order_num', 'description', 'valid')
        sequence = ('title', 'position', 'image','link_url','order_num', 'description', 'valid','actions')
        order_by = '-order_num'




