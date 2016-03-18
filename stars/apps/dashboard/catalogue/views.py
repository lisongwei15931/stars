#!/usr/bin/env python
# encoding: utf-8


from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from oscar.apps.dashboard.catalogue.views import (
    ProductCreateUpdateView as CoreProductCreateUpdateView)
from oscar.core.loading import get_model

from stars.apps.dashboard.catalogue.forms import (
    LocalProductRecommendationFormSet, LocalProductConfigFormSet,
    LocalProductImageFormSet, LocalStockRecordFormSet, StockEnterForm)

from django.views import generic

Product = get_model('catalogue', 'Product')

StockEnter = get_model('platform', 'StockEnter')

class ProductCreateUpdateView(CoreProductCreateUpdateView):
    recommendations_formset = LocalProductRecommendationFormSet
    product_config_formset = LocalProductConfigFormSet
    image_formset = LocalProductImageFormSet
    stockrecord_formset = LocalStockRecordFormSet

    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {'category_formset': self.category_formset,
                         'image_formset': self.image_formset,
                         'recommended_formset': self.recommendations_formset,
                         'stockrecord_formset': self.stockrecord_formset,
                         'product_config_formset': self.product_config_formset}

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreateUpdateView, self).get_context_data(**kwargs)
        se = StockEnter.objects.filter(user=self.request.user,product=self.object).order_by('created_datetime')
        ctx['stock_enter']=se
        ctx['stock_enter_form']=StockEnterForm()
        return ctx

    def forms_valid(self, form, formsets):
        if self.creating:
            self.handle_adding_child(self.parent)
        else:
            self.object = form.save()

        for formset in formsets.values():
            if isinstance(formset, LocalStockRecordFormSet):
                current_form = formset.forms[0]
                current_stockrecord = current_form.save()
                current_stockrecord.price_excl_tax = 1000.00
                current_stockrecord.price_retail = 1000.00
                current_stockrecord.cost_price = 1000.00
                current_stockrecord.num_in_stock = 1000
                current_stockrecord.low_stock_threshold = 10
                current_stockrecord.save()
            else:
                formset.save()

        return HttpResponseRedirect(self.get_success_url())
