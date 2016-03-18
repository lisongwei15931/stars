# -*- coding: utf-8 -*-

import json

from django.shortcuts import render, redirect
from django.http import HttpResponse

from stars.apps.address.models import (Province, City, District, ReceivingAddress)
from stars.apps.customer.receiving_address.forms import ReceivingAddressForm


def get_location(request):

    province_id = request.GET.get('province_id', '')
    city_id = request.GET.get('city_id', '')
    result = {}
    if province_id:
        try:
            current_province = Province.objects.get(id=province_id)

            citys = current_province.city_set.all()
            citys_data = list(citys.values('id', 'name'))

            districts = District.objects.filter(city__province=current_province)
            districts_data = list(districts.values('id', 'name'))

            result = {'citys': citys_data, 'districts': districts_data}
        except:
            result = {'citys': [], 'districts': []}
    if city_id:
        try:
            current_city = City.objects.get(id=city_id)

            districts = current_city.district_set.all()
            districts_data = list(districts.values('id', 'name'))

            result = {'districts': districts_data}
        except:
            result = {'districts': []}
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def receiving_address(request):
    user = request.user
    current_receiving_addresses = ReceivingAddress.objects.filter(user=user).order_by('-is_default')
    context = {'frame_id': 'receiving_address',
               'current_receiving_addresses': current_receiving_addresses}
    return render(request, 'customer/receiving_address/receiving_address.html', context)


def receiving_address_add(request):
    user = request.user
    add = True
    if request.is_ajax():
        form = ReceivingAddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = user
            new_address.save()
            return HttpResponse('ok')
        else:
            print form.errors.as_json()
            result = {'html':str(form.errors)}
            return HttpResponse(form.errors.as_json(), content_type="application/json")
    elif request.method == 'POST':
        form = ReceivingAddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = user
            new_address.save()
            return redirect('customer:receiving_address')
    else:
        form = ReceivingAddressForm()
    context = {'form': form, 'add': add}
    return render(request, 'customer/receiving_address/receiving_address_addupdate.html', context)


def receiving_address_update(request, receiving_address_id):
    user = request.user
    try:
        current_receiving_addresses = ReceivingAddress.objects.get(id=receiving_address_id)
    except ReceivingAddress.DoesNotExist:
        return redirect('customer:receiving_address')
    if request.method == 'POST':
        form = ReceivingAddressForm(request.POST, instance=current_receiving_addresses)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = user
            new_address.save()
            return redirect('customer:receiving_address')
    else:
        form = ReceivingAddressForm(instance=current_receiving_addresses)
    context = {'form': form}
    return render(request, 'customer/receiving_address/receiving_address_addupdate.html', context)


def receiving_address_set_default(request, receiving_address_id):
    try:
        current_receiving_addresses = ReceivingAddress.objects.get(id=receiving_address_id)
        current_receiving_addresses.is_default = True
        current_receiving_addresses.save()
    except ReceivingAddress.DoesNotExist:
        return redirect('customer:receiving_address')
    return redirect('customer:receiving_address')


def receiving_address_delete(request, receiving_address_id):
    try:
        current_receiving_addresses = ReceivingAddress.objects.get(id=receiving_address_id)
        current_receiving_addresses.delete()
    except ReceivingAddress.DoesNotExist:
        return redirect('customer:receiving_address')
    return redirect('customer:receiving_address')
