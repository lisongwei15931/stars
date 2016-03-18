 # -*- coding: utf-8 -*-
from django.http import HttpResponseNotFound
from django.shortcuts import render
from rest_framework.views import APIView

from stars.apps.commission.models import ProductOrder


class PayResultView(APIView):

    def get(self, request, order_pk):
        user = request.user

        product_order = ProductOrder.objects.get(pk=order_pk, user=user)
        if product_order.status == 2:
            tpl = 'basket/basket_success.html'
        elif product_order.status == 3:
            tpl = 'basket/basket_error.html'
        else:
            return HttpResponseNotFound()

        ctx = {}

        return render(request,tpl, ctx)

