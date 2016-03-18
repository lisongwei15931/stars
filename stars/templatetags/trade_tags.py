#coding=utf-8

from django import template
from stars.apps.commission.models import UserMoneyChange
from stars.apps.catalogue.models import Product
from stars.apps.commission.models import CommissionBuy, CommissionSale
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from datetime import datetime, timedelta

register = template.Library()


@register.filter
def charge(value):
    '''
    #成交手续费
    '''
    try :
        charge = UserMoneyChange.objects.get(trade_type=15, status=2, trade_no=value)
        price = charge.price
    except UserMoneyChange.DoesNotExist:
        price = '0.00'
    
    return price

@register.filter
def get_upc_title(value,key):
    '''
    #商品名称,UPC
    '''
    product = get_object_or_404(Product, pk=value)
    partner = product.stockrecords.first().partner.name
    if not product:
        upc = ''
        title = ''
        price = '0.00'
    upc = product.upc
    title = product.title
    price = product.stock_config_product.opening_price
    if key == 'title':
        return title
    if key == 'upc':
        return upc
    if key == 'partner':
        return partner
    if key == 'price':
        return price


@register.filter
def subtract(value):
    '''
    #减去商品上市价
    '''
    product = get_object_or_404(Product, pk=value['product'])
    price = product.stock_config_product.opening_price
    if not price :
        price = 0.00

    return round(price-value['unit_price'],2)

@register.filter
def current_trader(value,key):
    product = get_object_or_404(Product, pk=value)
    quantity = 0

    if key == 'buy':
        buy_q = CommissionBuy.objects.filter(status__in=[2,3], product=product).\
            aggregate(q=Sum(F('quantity')-F('uncomplete_quantity')))
        quantity = buy_q['q'] if buy_q['q'] else 0

    if key == 'sale':
        sale_q = CommissionSale.objects.filter(status__in=[2,3], product=product).\
            aggregate(q=Sum(F('quantity')-F('uncomplete_quantity')))
        quantity = sale_q['q'] if sale_q['q'] else 0

    return quantity

@register.filter
def close_trader(value,key):
    product = get_object_or_404(Product,pk=value)
    quantity = 0

    if key == 'td':
        try:
            close_q = CommissionBuy.objects.filter(status__in=[1,2], product=product).\
                 aggregate(q=Sum('uncomplete_quantity'))
            quantity = close_q['q'] if close_q['q'] else 0
        except:
            pass

    if key == 'tn':
        try:
            today = datetime.today().date()
            t_n = product.stock_config_product.t_n
            able_date = today - timedelta(days=t_n)
            close_q = CommissionBuy.objects.filter(status__in=[2,3], product=product, created_datetime__gte=able_date).\
                 aggregate(q=Sum(F('quantity')-F('uncomplete_quantity')))
            quantity = close_q['q'] if close_q['q'] else 0
        except:
            pass

    return quantity






