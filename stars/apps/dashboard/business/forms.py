#coding=utf-8
from django import forms
from stars.apps.pickup_admin.models import StoreInComeApply,APPLY_STATUS
from oscar.core.loading import get_model
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from oscar.core.compat import get_user_model
from stars.apps.commission.models import PickupDetail

User = get_user_model()
Partner = get_model('partner', 'Partner')
Product = get_model('catalogue','Product')
StockEnter = get_model('platform','StockEnter')

STATUS_CHOICES = (
    ('1', u'全部'), ('2', u'已关联'), ('3', u'未关联')
)

class ProductSearchForm(forms.Form):
    product = forms.CharField(required=False, label=u'商品名称')
    upc = forms.CharField(required=False, label=u'商品代码')
    associate_status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label=u'关联状态')
    trader = forms.CharField(required=False, label=u'已关联交易员')


class ProductTraderForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['trader', ]

    def __init__(self, *args, **kwargs):
        super(ProductTraderForm, self).__init__(*args, **kwargs)
        # filter traders
        trader_field = self.fields['trader']
        if self.instance:
            stockrecords = self.instance.stockrecords.all()
            if stockrecords:
                available_users = stockrecords[0].partner.users.filter(userprofile__role='trader')
                trader_field.queryset = available_users


class StoreInComeForm(forms.ModelForm):
    class Meta:
        model = StoreInComeApply
        fields = ['isp','product', 'pickup_addr', 'c_quantity',
                  'quantity','telephone', 'desc']
        widgets = {
                  'isp':forms.HiddenInput(),
                  }


class StoreInComeDealForm(forms.ModelForm):
    class Meta:
        model = StoreInComeApply
        fields = ['c_quantity',
                  'quantity', 'damaged_quantity', 'lose_quantity',
                  'status', 'refuse_desc']
    def __init__(self, *args, **kwargs):
        super(StoreInComeDealForm, self).__init__(*args, **kwargs)
        c_quantity_field = self.fields['c_quantity']
        c_quantity_field.widget.attrs = {'readonly': 'readonly'}
        quantity_field = self.fields['quantity']
        quantity_field.widget.attrs = {'readonly': 'readonly'}
        damaged_quantity_field = self.fields['damaged_quantity']
        damaged_quantity_field.widget.attrs = {'readonly': 'readonly'}
        lose_quantity_field = self.fields['lose_quantity']
        lose_quantity_field.widget.attrs = {'readonly': 'readonly'}
    def clean_refuse_desc(self):
        status = self.cleaned_data.get('status', None)
        refuse_desc = self.cleaned_data.get('refuse_desc', None)
        if status == '2' and (not refuse_desc):
            raise ValidationError(u'请填写驳回原因。')
        if status != '2' and refuse_desc:
            raise ValidationError(u'没有驳回，不可填写驳回原因。')
        return refuse_desc

#===============================================================================
#     #判断商品UPC是否正确。
#
#     def clean_product(self):
#         product = self.cleaned_data['product']
#
#         products = Product.objects.all().values_list('upc',flat=True)
#
#         if product not in products :
#             raise forms.ValidationError(u'没有该商品UPC')
#         return product
#
#===============================================================================

class BusinessProductForm(forms.ModelForm):
    class Meta:
        model = StockEnter
        fields = ['product','number','quantity','desc']

class SearchStoreInComeForm(forms.Form):
    STATUS_CHOICES = (
        ('', u'全部'),
    ) + APPLY_STATUS
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')
    pickup_addr = forms.CharField(required=False, label=u'自提点')
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label=u'审核状态',
                               widget=forms.Select(attrs={"style":"width:50px;"}))

class SearchProductApplyForm(forms.Form):
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')

class SearchPickProductForm(forms.Form):
    pickid = forms.CharField(required=False,label=u'提货单')
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')

class SearchBusinessInProductForm(forms.Form):
    ENTER_STATUS = (
        ('', u'请选择'),
        ('1', u'待审核'), ('2', u'已驳回'), ('3', u'已通过')
    )
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')
    status = forms.ChoiceField(required=False, choices=ENTER_STATUS, label=u'状态',
                               widget=forms.Select(attrs={"style":"width:50px;"}))


class SearchBusinessStockEnterDealForm(forms.Form):
    ENTER_STATUS = (
        ('', u'请选择'),
        ('1', u'待审核'), ('2', u'已驳回'), ('3', u'已通过')
    )
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')
    user = forms.CharField(required=False, label=u'申请人')
    status = forms.ChoiceField(required=False, choices=ENTER_STATUS, label=u'状态',
                               widget=forms.Select(attrs={"style":"width:50px;"}))


class BusinessStockEnterDealForm(forms.ModelForm):

    class Meta:
        model = StockEnter
        fields = ['status', 'refuse_desc']
    def clean_refuse_desc(self):
        status = self.cleaned_data.get('status', None)
        refuse_desc = self.cleaned_data.get('refuse_desc', None)
        if status == '2' and (not refuse_desc):
            raise ValidationError(u'请填写驳回原因。')
        if status != '2' and refuse_desc:
            raise ValidationError(u'没有驳回，不可填写驳回原因。')
        return refuse_desc


class SearchBusinessStoreForm(forms.Form):
    upc = forms.CharField(required=False, label=u'商品代码')
    product = forms.CharField(required=False, label=u'商品名称')
    pickup_addr = forms.CharField(required=False, label=u'自提点')

class SearchOutStoreForm(SearchBusinessStoreForm):
    STATUS_CHOICES = (('',u'全部'),  (1,'自提'),
        (2,'自提点代运'),
        (3,'厂商发货'),)
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label=u'提货类型')

class SearchSaleForm(SearchProductApplyForm):
    STATUS_CHOICES = (('',u'全部'),(1,'购买'),
        (2,'进货'),)
    #isp = forms.CharField(required=False,label=u'商家名称')
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label=u'销售类型')
    begin_date = forms.DateField(required=False,label=u'开始日期',widget=forms.DateInput(attrs=\
                                {'placeholder':'YYYY-mm-dd'}))
    end_date = forms.DateField(required=False,label=u'结束日期',widget= forms.DateInput(attrs=\
                               {'placeholder':'YYYY-mm-dd'}))
    


class SearchBusinessForm(SearchProductApplyForm):
    business = forms.CharField(required=False,label=u'商家名称')
    price = forms.IntegerField(required=False,label=u'指定市价')
    begin_date = forms.DateField(required=False,label=u'开始日期',widget=forms.DateInput(attrs=\
                                {'placeholder':'YYYY-mm-dd'}))
    end_date = forms.DateField(required=False,label=u'结束日期',widget= forms.DateInput(attrs=\
                               {'placeholder':'YYYY-mm-dd'}))


class BusinessLoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                self._errors['username'] = self.error_class([u'用户名/密码错误'])
            elif not self.user_cache.is_active:
                self._errors['username'] = self.error_class([u'此用户已经被删除'])
            elif not self.user_cache.is_staff:
                self._errors['username'] = self.error_class([u'您无权登录管理平台'])
            else:
                try:
                    current_userprofile = self.user_cache.userprofile
                    if not current_userprofile.is_member_unit():
                        self._errors['username'] = self.error_class([u'您不是会员单位用户'])
                    else :
                        user = current_userprofile.user
                        jys = user.partners.count()
                        if not jys or jys == 0:
                            self._errors['username']=self.error_class([u'没有绑定会员单位,请联系管理员'])
                        else:
                            if jys > 1 :
                                self._errors['username']=self.error_class([u'绑定了多个会员单位,请联系管理员'])

                except:
                    self._errors['username'] = self.error_class([u'您无权登录管理平台'])

        return self.cleaned_data


class TraderLoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                self._errors['username'] = self.error_class([u'用户名/密码错误'])
            elif not self.user_cache.is_active:
                self._errors['username'] = self.error_class([u'此用户已经被删除'])
            elif not self.user_cache.is_staff:
                self._errors['username'] = self.error_class([u'您无权登录管理平台'])
            else:
                try:
                    current_userprofile = self.user_cache.userprofile
                    if not current_userprofile.is_trader():
                        self._errors['username'] = self.error_class([u'您不是交易员用户'])
                    else :
                        user = current_userprofile.user
                        jys = user.partners.count()
                        if not jys or jys == 0 :
                            self._errors['username']=self.error_class([u'没有绑定会员单位,请联系管理员'])
                        else:
                            if jys > 1 :
                                self._errors['username']=self.error_class([u'绑定了多个会员单位,请联系管理员'])
                except:
                    self._errors['username'] = self.error_class([u'您无权登录管理平台'])

        return self.cleaned_data


class PartnerUserSearchForm(forms.Form):
    ROLE_CHOICE = (('',u'全部'),('member', u'普通会员'),
        ('member_unit', u'会员单位'),
        ('trader', u'交易员'),('extra_role', u'其它角色'),)
    userrole = forms.ChoiceField(required=False, choices=ROLE_CHOICE, label=u'用户类型')
    
class ExpressSendForm(forms.ModelForm):
    class Meta:
        model = PickupDetail
        fields = ['status','logistics_company','logistics_no','refuse_desc']

    def __init__(self, deal_type, *args, **kwargs):
        super(ExpressSendForm, self).__init__(*args, **kwargs)
        if deal_type == 'pickup':
            status_field = self.fields['status']
            if status_field:
                status_field.choices =((1, u'未提货'), (2, u'已提货'), (3, u'已驳回'), (4, u'未发货'))
        elif deal_type == 'express':
            status_field = self.fields['status']
            if status_field:
                status_field.choices =((3, u'已驳回'), (4, u'未发货'), (5, u'已发货'))

    def clean_refuse_desc(self):
        status = self.cleaned_data.get('status', None)
        refuse_desc = self.cleaned_data.get('refuse_desc', None)
        if status == 3 and (not refuse_desc):
            raise ValidationError(u'请填写驳回原因。')
        if status != 3 and refuse_desc:
            raise ValidationError(u'没有驳回，不可填写驳回原因。')
        return refuse_desc
    
    def clean_logistics_company(self):
        status = self.cleaned_data.get('status', None)
        logistics_company = self.cleaned_data.get('logistics_company',None)
        
        if status == 5 and (not logistics_company) :
            raise ValidationError(u'请填写货运/快递公司')
        if status != 5 and logistics_company :
            raise ValidationError(u'不是发货状态')
        return logistics_company
    
    def clean_logistics_no(self):
        status = self.cleaned_data.get('status',None)
        logistics_no = self.cleaned_data.get('logistics_no',None)
        
        if status == 5 and (not logistics_no) :
            raise ValidationError(u'请填写货运/快递单号')
        if status != 5 and logistics_no :
            raise ValidationError(u'不是发货状态')
        return logistics_no
        
        
