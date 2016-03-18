#coding=utf-8
from django import forms
from oscar.core.loading import get_model

from stars.apps.commission.models import COMMISSION_BUY_TYPE, \
    COMMISSION_SALE_TYPE
import datetime

Product = get_model('catalogue', 'Product')


class CommissionBuyForm(forms.Form):
    product = forms.ModelChoiceField(
        label='商品:',
        empty_label='选择商品',
        queryset=Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).distinct())
    price = forms.FloatField(label='价格:')
    quantity = forms.IntegerField(label='数量:')
    c_type = forms.ChoiceField(label='类型:',choices=COMMISSION_BUY_TYPE)
    

class CommissionSaleForm(forms.Form):
    product = forms.ModelChoiceField(
        label='商品:',
        empty_label='选择商品',
        queryset=Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).distinct())
    price = forms.FloatField(label='价格:')
    quantity = forms.IntegerField(label='数量:')
    c_type = forms.ChoiceField(label='类型:',choices=COMMISSION_SALE_TYPE)