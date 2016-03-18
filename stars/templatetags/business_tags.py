#coding=utf-8
from django import template
from oscar.core.loading import get_model
from django.db.models import Sum

register = template.Library()

StockEnter = get_model('platform','StockEnter')
@register.filter
def get_business_quantity(value):
    try:
        st = StockEnter.objects.filter(product=value).values('product').aggregate(q=Sum('quantity'))
        if st['q']:
            return st['q']
        else :
            return u'—'.encode('utf-8')     
    except:
        return u'—'.encode('utf-8')

@register.filter
def get_lost(value,q):
    try:
        st = StockEnter.objects.filter(product=value).values('product').aggregate(q=Sum('quantity'))
        if st['q']:
            sq = st['q']
        else:
            sq = 0
        
        if sq<q:
            return sq-q
        else :
            return u'—'.encode('utf-8')
        
    except:
        pass    
    
@register.filter
def get_status(value):
    if value == 2:
        return u'已提货'
    else:
        return u'未提货'
    
@register.filter
def get_pickup_type(value):
    if value == 1:
        return u'自提'
    elif value == 2:
        return u'自提点代运'
    else :
        return u'厂商发货'
@register.filter
def get_yet_pickup(value,value2):
    return value-value2
    