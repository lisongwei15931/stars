#coding=utf-8

from django import forms
from oscar.core.loading import get_model


class BaseSearchForm(forms.Form):
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')
    

class CommissionQuerySearchForm(BaseSearchForm):
    commission_no = forms.CharField(required=False, label=u'委托编号')
    isp = forms.CharField(required=False, label=u'交易商名称')
    
class CommissionQueryAllSearchForm(CommissionQuerySearchForm):
    begin_date = forms.DateField(required=False,label=u'开始日期',widget=forms.DateInput(attrs=\
                                {'placeholder': 'YYYY-mm-dd'}))
    end_date = forms.DateField(required=False,label=u'结束日期',widget=forms.DateInput(attrs=\
                               {'placeholder': 'YYYY-mm-dd'}))
    
class TradecompleteQuerySearchForm(BaseSearchForm):
    trade_no = forms.CharField(required=False, label=u'成交编号')
    isp = forms.CharField(required=False, label=u'交易商名称')
    
class TradecompleteQueryAllSearchForm(TradecompleteQuerySearchForm):
    begin_date = forms.DateField(required=False,label=u'开始日期',widget=forms.DateInput(attrs=\
                                {'placeholder': 'YYYY-mm-dd'}))
    end_date = forms.DateField(required=False,label=u'结束日期',widget=forms.DateInput(attrs=\
                               {'placeholder': 'YYYY-mm-dd'}))

class HoldProductSearchForm(BaseSearchForm):
    isp = forms.CharField(required=False, label=u'交易商名称')

class UserSearchForm(forms.Form):
    ROLE_CHOICE = (('',u'------'), ('member', u'会员'), ('ISP', u'厂商'), ('dashboard_admin', u'后台管理员'),
        ('warehouse_staff', u'仓库人员'), ('member_unit', u'会员单位'),
        ('trader', u'交易员'))
    user = forms.CharField(required=False, label=u'用户')
    role = forms.ChoiceField(required=False, choices=ROLE_CHOICE, label=u'用户角色')

class CapitalSearchForm(UserSearchForm):
    begin_date = forms.DateField(required=False,label=u'开始日期',widget=forms.DateInput(attrs=\
                                {'placeholder': 'YYYY-mm-dd'}))
    end_date = forms.DateField(required=False,label=u'结束日期',widget=forms.DateInput(attrs=\
                               {'placeholder': 'YYYY-mm-dd'}))