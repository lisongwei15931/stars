# -*- coding: utf-8 -*-s

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django import forms
from django.core import exceptions
from django.db.models.manager import Manager
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.forms import modelform_factory
from django.db.models import Max
from oscar.apps.dashboard.catalogue.forms import (ProductForm as CoreProductForm,
    ProductSearchForm as CoreProductSearchForm,
    ProductImageForm as CoreProductImageForm,
    ProductRecommendationForm, ProductRecommendation,
    _attr_text_field, _attr_textarea_field, _attr_integer_field,
    _attr_boolean_field, _attr_float_field, _attr_date_field, _attr_option_field,
    _attr_file_field, _attr_image_field, _attr_entity_field, _attr_numeric_field)
from oscar.core.loading import get_model



Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')
StockProductConfig = get_model('commission', 'StockProductConfig')
StockEnter = get_model('platform', 'StockEnter')
StockRecord = get_model('partner', 'StockRecord')


class ProductForm(CoreProductForm):
    FIELD_FACTORIES = {
        "text": _attr_text_field,
        "richtext": _attr_textarea_field,
        "integer": _attr_integer_field,
        "boolean": _attr_boolean_field,
        "float": _attr_float_field,
        "date": _attr_date_field,
        "option": _attr_option_field,
        "entity": _attr_entity_field,
        "numeric": _attr_numeric_field,
        "file": _attr_file_field,
        "image": _attr_image_field,
    }
    description = forms.CharField(widget=CKEditorUploadingWidget(attrs={'class':'no-widget-init'}))

    class Meta:
        model = Product
        fields = [
            'title', 'upc', 'description', 'is_discountable', 'structure', 'is_on_shelves',
            'selection_reputation', 'new_listing', 'featured_hot', 'hot_deals', 'opening_date', 'product_long_image']
        widgets = {
            'structure': forms.HiddenInput()
        }

    def set_initial_attribute_values(self, product_class, kwargs):
        """
        Update the kwargs['initial'] value to have the initial values based on
        the product instance's attributes
        """
        instance = kwargs.get('instance')
        if instance is None:
            return
        for attribute in product_class.attributes.all():
            try:
                value = instance.attribute_values.get(
                    attribute=attribute).value
            except exceptions.ObjectDoesNotExist:
                pass
            else:
                if isinstance(value, Manager):
                    value = value.all()
                kwargs['initial']['attr_%s' % attribute.code] = value


class ProductImageForm(CoreProductImageForm):
    def has_changed(self):
        changed = super(ProductImageForm, self).has_changed()
        if not self.instance.pk:
            return changed
        return changed or self.instance.display_order != self.get_display_order()

    def get_display_order(self):
        if self.instance.display_order:
            return self.instance.display_order
        else:
            if ProductImage.objects.filter(product=self.instance.product):
                max_display_order = ProductImage.objects.filter(product=self.instance.product). \
                                        aggregate(Max('display_order'))['display_order__max']
                max_display_order += 1
            else:
                max_display_order = 0
            return max_display_order


LocalBaseProductImageFormSet = inlineformset_factory(
    Product, ProductImage, form=ProductImageForm, extra=2)


class LocalProductImageFormSet(LocalBaseProductImageFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(LocalProductImageFormSet, self).__init__(*args, **kwargs)


class StockRecordForm(forms.ModelForm):

    def __init__(self, product_class, user, *args, **kwargs):
        self.user = user
        super(StockRecordForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StockRecord
        fields = [
            'partner', 'partner_sku',
        ]


LocalBaseStockRecordFormSet = inlineformset_factory(
    Product, StockRecord, form=StockRecordForm, max_num=1, can_delete=False)


class LocalStockRecordFormSet(LocalBaseStockRecordFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        self.user = user
        self.require_user_stockrecord = not user.is_staff
        self.product_class = product_class
        super(LocalStockRecordFormSet, self).__init__(*args, **kwargs)
        self.set_initial_data()

    def set_initial_data(self):
        """
        If user has only one partner associated, set the first
        stock record's partner to it. Can't pre-select for staff users as
        they're allowed to save a product without a stock record.

        This is intentionally done after calling __init__ as passing initial
        data to __init__ creates a form for each list item. So depending on
        whether we can pre-select the partner or not, we'd end up with 1 or 2
        forms for an unbound form.
        """
        if self.require_user_stockrecord:
            try:
                user_partner = self.user.partners.get()
            except (exceptions.ObjectDoesNotExist,
                    exceptions.MultipleObjectsReturned):
                pass
            else:
                partner_field = self.forms[0].fields.get('partner', None)
                if partner_field and partner_field.initial is None:
                    partner_field.initial = user_partner

    def _construct_form(self, i, **kwargs):
        kwargs['product_class'] = self.product_class
        kwargs['user'] = self.user
        return super(LocalStockRecordFormSet, self)._construct_form(
            i, **kwargs)

    def clean(self):
        """
        If the user isn't a staff user, this validation ensures that at least
        one stock record's partner is associated with a users partners.
        """
        if any(self.errors):
            return
        if self.require_user_stockrecord:
            stockrecord_partners = set([form.cleaned_data.get('partner', None)
                                        for form in self.forms])
            user_partners = set(self.user.partners.all())
            if not user_partners & stockrecord_partners:
                raise exceptions.ValidationError(
                    _("At least one stock record must be set to a partner that"
                      " you're associated with."))


class ProductConfigForm(forms.ModelForm):
    class Meta:
        model = StockProductConfig
        fields = [
             'quote','max_buy_num','max_deal_num','self_pick_or_express','opening_price','once_max_num','max_num','pickup_price','express_price','scomm','pickup_addr','sale_num'
             ,'min_price','ud_up_range','ud_down_range','min_bnum','min_snum','distribution_pickup_addr','pickup_addr']

class StockEnterForm(forms.ModelForm):
#     def __init__(self, product_class, user, *args, **kwargs):
#         # The user kwarg is not used by stock StockRecordForm. We pass it
#         # anyway in case one wishes to customise the partner queryset
#         initial = kwargs.get('initial', {})
#         initial['user'] = user
#         kwargs['initial'] = initial
#         super(StockEnterForm, self).__init__(*args, **kwargs)
    class Meta:
        model = StockEnter
        fields = [
             'user','product','quantity','desc']

LocalBaseProductRecommendationFormSet = inlineformset_factory(
    Product, ProductRecommendation, form=ProductRecommendationForm,
    extra=7, fk_name="primary")

LocalBaseProductConfigFormSet = inlineformset_factory(
    Product, StockProductConfig, form=ProductConfigForm,max_num=1,can_delete=False)
#
# StockEnterFormSet = inlineformset_factory(
#     Product, StockEnter, form=StockEnterForm,extra=1,can_delete=False)




class LocalProductRecommendationFormSet(LocalBaseProductRecommendationFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(LocalProductRecommendationFormSet, self).__init__(*args, **kwargs)

class LocalProductConfigFormSet(LocalBaseProductConfigFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(LocalProductConfigFormSet, self).__init__(*args, **kwargs)

# class LocalStockEnterFormSet(StockEnterFormSet):
#
#     def __init__(self, product_class, user, *args, **kwargs):
#         self.user=user
#         self.product_class = product_class
#         super(LocalStockEnterFormSet, self).__init__(*args, **kwargs)
#
#     def _construct_form(self, i, **kwargs):
#         kwargs['product_class'] = self.product_class
#         kwargs['user'] = self.user
#         return super(LocalStockEnterFormSet, self)._construct_form(
#             i, **kwargs)

class ProductSearchForm(CoreProductSearchForm):
    upc = forms.CharField(max_length=16, required=False, label=_(u'商品代码'))
    title = forms.CharField(
        max_length=255, required=False, label=_(u'商品名称'))
