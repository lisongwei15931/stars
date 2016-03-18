#!/usr/bin/env python
# encoding: utf-8


from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet

from oscar.apps.basket.forms import (BasketLineForm as CoreBasketLineForm,
    BaseBasketLineFormSet)
from oscar.core.loading import get_model
from oscar.forms import widgets

Line = get_model('basket', 'line')
Basket = get_model('basket', 'basket')
Product = get_model('catalogue', 'product')


class BasketLineForm(CoreBasketLineForm):
    class Meta:
        model = Line
        fields = ['quantity', 'buy_price']
        widgets = {
            'quantity': forms.TextInput(),
            'buy_price': forms.TextInput()
        }


BasketLineFormSet = modelformset_factory(
    Line, form=BasketLineForm, formset=BaseBasketLineFormSet, extra=0,
    can_delete=True)
