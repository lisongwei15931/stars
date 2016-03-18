# encoding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from oscar.core.loading import get_model
from oscar.core.compat import get_user_model

from stars.apps.pickup_admin.models import APPLY_STATUS

User = get_user_model()
PickupStore = get_model('pickup_admin', 'PickupStore')
StoreInCome = get_model('pickup_admin', 'StoreInCome')
StoreInComeApply = get_model('pickup_admin', 'StoreInComeApply')
PickupStatistics = get_model('pickup_admin', 'PickupStatistics')
PickupAddr = get_model('commission', 'PickupAddr')
PickupDetail = get_model('commission', 'PickupDetail')
PickupList = get_model('commission', 'PickupList')


class PickupStoreSearchForm(forms.Form):
    product = forms.CharField(required=False, label=u'商品名称')
    upc = forms.CharField(required=False, label=u'商品代码')
    pickup_addr = forms.CharField(required=False, label=u'提货点')


class PickupDetailSearchForm(forms.Form):
    pickup_list = forms.CharField(required=False, label=u'提货单号')
    pickup_captcha = forms.CharField(required=False, label=u'提货验证码')
    product = forms.CharField(required=False, label=u'商品名称')
    upc = forms.CharField(required=False, label=u'商品代码')


class StoreInComeApplySearchForm(forms.Form):
    STATUS_CHOICES = (
        ('', '------------'),
    ) + APPLY_STATUS

    product = forms.CharField(required=False, label=u'商品名称')
    upc = forms.CharField(required=False, label=u'商品代码')
    isp = forms.CharField(required=False, label=u'交易商')
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label=u'审核状态')
    '''
    apply_date_from = forms.DateTimeField(required=False, label=u'申请日期——起始')
    apply_date_to = forms.DateTimeField(required=False, label=u'申请日期——结束')
    '''


class StoreInComeApplyForm(forms.ModelForm):

    class Meta:
        model = StoreInComeApply
        fields = ['quantity', 'plan_income_date', 'damaged_quantity',
                  'lose_quantity']

    def __init__(self, *args, **kwargs):
        super(StoreInComeApplyForm, self).__init__(*args, **kwargs)
        plan_income_date_field = self.fields['plan_income_date']
        plan_income_date_field.widget.attrs = {'readonly': 'readonly'}
        quantity_field = self.fields['quantity']
        quantity_field.widget.attrs = {'readonly': 'readonly'}

    def clean_refuse_desc(self):
        status = self.cleaned_data.get('status', None)
        refuse_desc = self.cleaned_data.get('refuse_desc', None)
        if status == '2' and (not refuse_desc):
            raise ValidationError(u'请填写驳回原因。')
        if status != '2' and refuse_desc:
            raise ValidationError(u'没有驳回，不可填写驳回原因。')
        return refuse_desc


class StoreInComeSearchForm(forms.Form):
    product = forms.CharField(required=False, label=u'商品名称')
    upc = forms.CharField(required=False, label=u'商品代码')
    isp = forms.CharField(required=False, label=u'交易商')


class StoreInComeForm(forms.ModelForm):

    class Meta:
        model = StoreInCome
        exclude = ['c_quantity', 'build_from', 'build_date']

    def __init__(self, *args, **kwargs):
        super(StoreInComeForm, self).__init__(*args, **kwargs)
        producttion_date_field = self.fields['producttion_date']
        warehouse_rental_start_time_field = self.fields['warehouse_rental_start_time']

        producttion_date_field.widget.attrs = {'readonly': 'readonly'}
        warehouse_rental_start_time_field.widget.attrs = {'readonly': 'readonly'}


class PickupDetailForm(forms.ModelForm):

    class Meta:
        model = PickupDetail
        fields = ['status', 'refuse_desc']

    def __init__(self, deal_type, *args, **kwargs):
        super(PickupDetailForm, self).__init__(*args, **kwargs)
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


class PickupStatisticsSearchForm(forms.Form):
    product = forms.CharField(required=False, label=u'商品名称')
    upc = forms.CharField(required=False, label=u'商品代码')
    pickup_addr = forms.CharField(required=False, label=u'提货点')


class LoginForm(AuthenticationForm):

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
                    if not current_userprofile.is_warehouse_staff():
                        self._errors['username'] = self.error_class([u'您不是自提点管理员'])
                except:
                    self._errors['username'] = self.error_class([u'您无权登录管理平台'])

        return self.cleaned_data
