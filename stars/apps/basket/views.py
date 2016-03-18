# encoding: utf-8

import datetime
import json
import traceback

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import transaction
from stars.apps.customer.receiving_address.forms import ReceivingAddressForm
from django.db.models import Sum
from django.http import HttpResponse
from django.http import HttpResponseRedirect  
from django.shortcuts import redirect, render
from django.template import Context
from django.template.loader import get_template
from django.utils.http import is_safe_url
from oscar.apps.basket.views import (BasketView as CoreBasketView,
                                     BasketAddView as CoreBasketAddView)
from oscar.apps.customer.history import extract
from oscar.core.loading import get_model
from oscar.core.utils import safe_referrer
from rest_framework.views import APIView

from stars.apps.address.models import ReceivingAddress
from stars.apps.basket.forms import BasketLineFormSet, BasketLineForm
from stars.apps.catalogue.utils import open_close_date
from stars.apps.commission.models import UserPickupAddr, PickupAddr, ProductOrder, OrderInfo
from stars.apps.commission.views import new_commission_buy, DealException, order_commission
from stars.apps.tradingcenter.views import is_market_opening


Line = get_model('basket', 'Line')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue','Category')
Partner = get_model('partner', 'Partner')
UserBalance = get_model('commission', 'UserBalance')
UserMoneyChange = get_model('commission', 'UserMoneyChange')
SystemConfig = get_model('commission', 'SystemConfig')
PickupList = get_model('commission', 'PickupList')
PickupDetail = get_model('commission', 'PickupDetail')

class BasketView(CoreBasketView):
    formset_class = BasketLineFormSet
    form_class = BasketLineForm

    def get_success_url(self):
        try:
            if not is_market_opening():
                return reverse('tradingcenter:market_closed')
            all_lines = self.request.basket.lines.all()
            for line in all_lines:
                product = line.product
                c_type = 1
                user = self.request.user
                unit_price = line.buy_price
                quantity = line.quantity
                new_commission_buy(product,user,c_type,unit_price,quantity,quantity,1)
            self.request.basket.set_as_submitted()
            return reverse('basket:basket_success_view')
        except DealException,e:
            print e
            return reverse('customer:finance-ab-recharge')
        except:
            return reverse('basket:basket_error_view')
    def get_context_data(self, **kwargs):
        context = super(BasketView, self).get_context_data(**kwargs)
        all_lines = self.request.basket.lines.all()
        if all_lines:
            all_products = Product.objects.filter(id__in=all_lines.values_list('product', flat=True))
            all_products_ids = all_products.values_list('id', flat=True)
            all_recommended_products_ids = all_products.values_list('recommended_products', flat=True)
            recommended_products_ids = set(all_recommended_products_ids).difference(set(all_products_ids))
            if all_recommended_products_ids:
                all_recommended_products = Product.objects.filter(id__in=recommended_products_ids,opening_date__lte=datetime.datetime.now().date())
            else:
                all_recommended_products = []

            total_quantity = all_lines.aggregate(Sum('quantity')).get('quantity__sum')
            total_price = 0
            for line in all_lines:
                total_price += line.total_price
        else:
            all_recommended_products = []
            total_quantity = 0
            total_price = 0

        history_products = Product.objects.filter(id__in = extract(self.request),opening_date__lte=datetime.datetime.now().date())[:5]
        context['history_products'] = history_products
        context['all_recommended_products'] = all_recommended_products
        context['total_quantity'] = total_quantity
        context['total_price'] = total_price
        category_list = Category.objects.filter(depth=1).order_by('path')[:10]
        context['category_list']=category_list
        context['open_or_close'] = open_close_date()[0]
        context['open_close_msg'] = open_close_date()[1]

        return context


def line_quantity_set(request):
    line_id = request.GET.get('line_id', '')
    quantity = request.GET.get('quantity', '')
    if line_id and quantity:
        try:
            current_line = Line.objects.get(id=line_id)
            current_line.quantity = int(quantity)
            current_line.save()
        except:
            pass
        result = {'result': True}
    else:
        result = {'result': False}
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def line_buy_price_set(request):
    # import ipdb;ipdb.set_trace()
    line_id = request.GET.get('line_id', '')
    buy_price = request.GET.get('buy_price', '')
    if line_id and buy_price:
        try:
            current_line = Line.objects.get(id=line_id)
            current_line.buy_price = float(buy_price)
            current_line.save()
        except:
            pass
        result = {'result': True}
    else:
        result = {'result': False}
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def delete_line_view(request, pk):
    try:
        current_line = Line.objects.get(id=pk)
        current_line.delete()
    except:
        pass
    return redirect('basket:summary')


def clean_basket_view(request):
    current_basket = request.basket
    all_lines = current_basket.lines.all()
    all_lines.delete()
    return redirect('basket:summary')


def order_settlement_view(request):
    context = {}
    return render(request, 'basket/order_settlement.html', context)


class BuyView(CoreBasketAddView):
    def get_success_url(self):
        post_url = "/basket"
        if post_url and is_safe_url(post_url, self.request.get_host()):
            return post_url
        return safe_referrer(self.request, 'basket:summary')


def basket_success_view(request):
    context = {}
    return render(request, 'basket/basket_success.html', context)


def basket_error_view(request):
    context = {}
    return render(request, 'basket/basket_error.html', context)


class MoveToMyfavView(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']

        ln = Line.objects.get(id=pk)
        WishList = get_model('wishlists', 'WishList')
        WishList.objects.get_or_create(owner=request.user)[0].add(ln.product)
        ln.delete()

        return redirect('basket:summary')


def order_confirm(request):
    current_basket = request.basket
    all_lines = current_basket.lines.all()
    current_user = request.user
    current_address_list = ReceivingAddress.objects.filter(user=current_user).order_by('-is_default')
    current_product_list = Product.objects.filter(id__in=all_lines.values_list('product', flat=True))
    current_partner_list = Partner.objects.filter(id__in=current_product_list.values_list('stockrecords__partner'))
    form = ReceivingAddressForm()
    partner_line_list = []
    total_pickup_price = 0
    total_express_price = 0
    total_product_price = 0

    # choose pickup addr
    if request.is_ajax():
        pickup_addr_id = request.GET.get('pickup_addr_id', '')
        if pickup_addr_id:
            if pickup_addr_id == 'express':
                for partner in current_partner_list:
                    products = current_product_list.filter(stockrecords__partner=partner)
                    lines = all_lines.filter(product__in=products)
                    pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
                    total_pickup_price += pickup_price
                    express_price = sum([line.product.express_price * line.quantity for line in lines])
                    total_express_price += express_price
                    product_price = sum([line.total_price for line in lines])
                    total_product_price += product_price
                    partner_line = {'partner': partner,
                                    'lines': lines,
                                    'pickup_price': pickup_price,
                                    'express_price': express_price}
                    partner_line_list.append(partner_line)

                total_price = total_pickup_price + total_express_price + total_product_price
                product_num = all_lines.aggregate(Sum('quantity')).get('quantity__sum')

                user_pickup_addr_list = UserPickupAddr.objects.filter(user=current_user).order_by('-is_default')
                if user_pickup_addr_list.count() > 0:
                    default_user_pickup_addr = user_pickup_addr_list[0]
                    pickup_addr = default_user_pickup_addr.pickup_addr
                else:
                    pickup_addr = ''
                context = {'current_address_list': current_address_list,
                        'partner_line_list': partner_line_list,
                        'total_pickup_price': total_pickup_price,
                        'total_express_price': total_express_price,
                        'total_product_price': total_product_price,
                        'total_price': total_price,
                        'product_num': product_num,
                        'pickup_addr': pickup_addr,
                        'user': current_user}
                order_content_template = get_template('basket/partials/order_confirm_order_content.html')
                order_price_template = get_template('basket/partials/order_confirm_price.html')
                order_content_template_html = order_content_template.render(Context(context))
                order_price_template_html = order_price_template.render(Context(context))
                payload = {'order_content_template_html': order_content_template_html,
                           'order_price_template_html': order_price_template_html,
                           'express_num': 1,
                           'success': True, 'pickup_addr_id':''}
                return HttpResponse(json.dumps(payload), content_type="application/json")
            else:
                try:
                    pickup_addr = PickupAddr.objects.get(id=pickup_addr_id)
                    pickup_product_list = current_product_list.filter(stock_config_product__distribution_pickup_addr=pickup_addr)
                    express_product_list = current_product_list.exclude(id__in=pickup_product_list.values_list('id', flat=True))
                    current_partner_list = Partner.objects.filter(id__in=express_product_list.values_list('stockrecords__partner'))
                    express_num = 0
                    if express_product_list:
                        for partner in current_partner_list:
                            products = express_product_list.filter(stockrecords__partner=partner)
                            lines = all_lines.filter(product__in=products)
                            pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
                            total_pickup_price += pickup_price
                            express_price = sum([line.product.express_price * line.quantity for line in lines])
                            total_express_price += express_price
                            product_price = sum([line.total_price for line in lines])
                            total_product_price += product_price
                            partner_line = {'partner': partner,
                                            'lines': lines,
                                            'pickup_price': pickup_price,
                                            'express_price': express_price}
                            partner_line_list.append(partner_line)
                            express_num += lines.aggregate(Sum('quantity')).get('quantity__sum')
                    pickup_line_list = []
                    if pickup_product_list:
                        lines = all_lines.filter(product__in=pickup_product_list)
                        pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
                        total_pickup_price += pickup_price
                        product_price = sum([line.total_price for line in lines])
                        total_product_price += product_price
                        pickup_line = {'lines': lines,
                                    'pickup_price': pickup_price}
                        pickup_line_list.append(pickup_line)
                    total_price = total_pickup_price + total_express_price + total_product_price
                    product_num = all_lines.aggregate(Sum('quantity')).get('quantity__sum')

                    order_content_template = get_template('basket/partials/order_confirm_order_content.html')
                    order_price_template = get_template('basket/partials/order_confirm_price.html')
                    context = {'current_address_list': current_address_list,
                            'partner_line_list': partner_line_list,
                            'pickup_line_list': pickup_line_list,
                            'total_pickup_price': total_pickup_price,
                            'total_express_price': total_express_price,
                            'total_product_price': total_product_price,
                            'total_price': total_price,
                            'product_num': product_num,
                            'express_num': express_num,
                            'pickup_addr': pickup_addr,
                            'user': current_user}
                    order_content_template_html = order_content_template.render(Context(context))
                    order_price_template_html = order_price_template.render(Context(context))
                    payload = {'order_content_template_html': order_content_template_html,
                            'order_price_template_html': order_price_template_html,
                            'express_num': express_num,
                            'success': True, 'pickup_addr_id':pickup_addr.id}
                    return HttpResponse(json.dumps(payload), content_type="application/json")
                except:
                    pass
    for partner in current_partner_list:
        products = current_product_list.filter(stockrecords__partner=partner)
        lines = all_lines.filter(product__in=products)
        pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
        total_pickup_price += pickup_price
        express_price = sum([line.product.express_price * line.quantity for line in lines])
        total_express_price += express_price
        product_price = sum([line.total_price for line in lines])
        total_product_price += product_price
        partner_line = {'partner': partner,
                        'lines': lines,
                        'pickup_price': pickup_price,
                        'express_price': express_price}
        partner_line_list.append(partner_line)

    total_price = total_pickup_price + total_express_price + total_product_price
    product_num = all_lines.aggregate(Sum('quantity')).get('quantity__sum')

    user_pickup_addr_list = UserPickupAddr.objects.filter(user=current_user).order_by('-is_default')
    if user_pickup_addr_list.count() > 0:
        default_user_pickup_addr = user_pickup_addr_list[0]
        pickup_addr = default_user_pickup_addr.pickup_addr
    else:
        pickup_addr = ''
    context = {'current_address_list': current_address_list,
               'partner_line_list': partner_line_list,
               'total_pickup_price': total_pickup_price,
               'total_express_price': total_express_price,
               'total_product_price': total_product_price,
               'total_price': total_price,
               'product_num': product_num,
               'pickup_addr': pickup_addr,
               'user': current_user,'form':form}
    if request.method == 'POST':
        pickup_type = int(request.POST.get('pickup_type', 2))
        if pickup_type == 1:
            pickup_address_id = request.POST.get('pickup_address_id', '')
            if pickup_address_id:
                pass
        receiving_address_id = request.POST.get('receiving_address_id', '')
        try:
            current_receiving_address = ReceivingAddress.objects.get(id=receiving_address_id)
            if pickup_type == 2:
                total_pickup_price = 0
                total_express_price = 0
                total_product_price = 0
                for partner in current_partner_list:
                    products = current_product_list.filter(stockrecords__partner=partner)
                    lines = all_lines.filter(product__in=products)
                    pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
                    total_pickup_price += pickup_price
                    express_price = sum([line.product.express_price * line.quantity for line in lines])
                    total_express_price += express_price
                    product_price = sum([line.total_price for line in lines])
                    total_product_price += product_price
                    partner_line = {'partner': partner,
                                    'lines': lines,
                                    'pickup_price': pickup_price,
                                    'express_price': express_price}
                    partner_line_list.append(partner_line)
                total_price = total_pickup_price + total_express_price + total_product_price
                product_order = ProductOrder()
                product_order.user=current_user
                product_order.amount=total_price
                product_order.pickup_type=pickup_type
                product_order.status=0
                product_order.province=current_receiving_address.province
                product_order.city=current_receiving_address.city
                product_order.addr=current_receiving_address.address
                product_order.receive_addr = current_receiving_address
                product_order.product_price = total_product_price
                product_order.express_fee = total_express_price
                product_order.pickup_fee = total_pickup_price
                product_names = [product.title for product in current_product_list]
                product_order.detail = " ".join(product_names)
                product_order.custom_save()
                for current_product in current_product_list:
                    line = all_lines.get(product=current_product)
                    OrderInfo.objects.create(product_order=product_order,product=current_product,product_num=line.quantity,price=line.buy_price)
                current_basket.submit()
                redirect_url = "/basket/pay-order/%s/"%product_order.id
                return HttpResponseRedirect(redirect_url)
            else:
                pass
#                 try:
#                     pickup_addr = PickupAddr.objects.get(id=pickup_address_id)
#                     pickup_product_list = current_product_list.filter(stock_config_product__distribution_pickup_addr=pickup_addr)
#                     express_product_list = current_product_list.exclude(id__in=pickup_product_list.values_list('id', flat=True))
#                     current_partner_list = Partner.objects.filter(id__in=express_product_list.values_list('stockrecords__partner'))
#                     express_num = 0
#                     if express_product_list:
#                         total_pickup_price = 0
#                         total_express_price = 0
#                         total_product_price = 0
#                         for partner in current_partner_list:
#                             products = express_product_list.filter(stockrecords__partner=partner)
#                             lines = all_lines.filter(product__in=products)
#                             pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
#                             total_pickup_price += pickup_price
#                             express_price = sum([line.product.express_price * line.quantity for line in lines])
#                             total_express_price += express_price
#                             product_price = sum([line.total_price for line in lines])
#                             total_product_price += product_price
#                             partner_line = {'partner': partner,
#                                             'lines': lines,
#                                             'pickup_price': pickup_price,
#                                             'express_price': express_price}
#                             partner_line_list.append(partner_line)
#                             express_num += lines.aggregate(Sum('quantity')).get('quantity__sum')
#                         total_price = total_pickup_price + total_express_price + total_product_price
#                         product_order = ProductOrder()
#                         product_order.user=current_user
#                         product_order.amount=total_price
#                         product_order.pickup_type=2
#                         product_order.status=0
#                         product_order.province=current_receiving_address.province
#                         product_order.city=current_receiving_address.city
#                         product_order.addr=current_receiving_address.address
#                         product_order.custom_save()
#                         for current_product in express_product_list:
#                             line = all_lines.get(product=current_product)
#                             OrderInfo.objects.create(product_order=product_order,product=current_product,product_num=line.quantity,price=line.buy_price)
#                     pickup_line_list = []
#                     if pickup_product_list:
#                         total_pickup_price = 0
#                         total_express_price = 0
#                         total_product_price = 0
#                         lines = all_lines.filter(product__in=pickup_product_list)
#                         pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
#                         total_pickup_price += pickup_price
#                         product_price = sum([line.total_price for line in lines])
#                         total_product_price += product_price
#                         pickup_line = {'lines': lines,
#                                     'pickup_price': pickup_price}
#                         pickup_line_list.append(pickup_line)
#                         total_price = total_pickup_price + total_product_price
#                         product_order = ProductOrder()
#                         product_order.user=current_user
#                         product_order.amount=total_price
#                         product_order.pickup_type=1
#                         product_order.status=0
#                         product_order.province=current_receiving_address.province
#                         product_order.city=current_receiving_address.city
#                         product_order.addr=current_receiving_address.address
#                         product_order.pickup_addr = pickup_addr
#                         product_order.custom_save()
#                         for current_product in pickup_product_list:
#                             line = all_lines.get(product=current_product)
#                             OrderInfo.objects.create(product_order=product_order,product=current_product,product_num=line.quantity,price=line.buy_price)
#                     current_basket.submit()
#                 except:
#                     raise
        except:
            traceback.print_exc()
    return render(request, 'basket/order_confirm.html', context)


def pay_order(request, pk):
    if request.method == 'GET':
        product_order = ProductOrder.objects.get(id=pk)
        user_balance = UserBalance.objects.get(user=request.user)
        context = {'product_order':product_order,'user_balance':user_balance}
        return render(request, 'basket/pay_order.html', context)
    elif request.method == 'POST':
        product_order = ProductOrder.objects.get(id=pk)
        user_balance = UserBalance.objects.get(user=request.user)
        ctx = {'product_order':product_order,'user_balance':user_balance}
        flag = True
        try:
            user = request.user
            pay_pwd = request.POST.get('pay_pwd','')
            price = float(request.POST.get('price',0))
            if user_balance.balance < price:
                flag = False
                ctx['balance_err_msg'] = u'余额不足'
            if not check_password(pay_pwd, user.userprofile.pay_pwd):
                flag = False
                ctx['pwd_err_msg'] = u'密码不匹配'
            with transaction.atomic():
                if flag:
                    order_express_money_change = UserMoneyChange()
                    order_express_money_change.user = user
                    order_express_money_change.trade_type = 16
                    order_express_money_change.status = 2
                    order_express_money_change.price = product_order.express_fee
                    order_express_money_change.order_no = product_order.order_no
                    order_express_money_change.custom_save()
                    order_pickup_money_change = UserMoneyChange()
                    order_pickup_money_change.user = user
                    order_pickup_money_change.trade_type = 17
                    order_pickup_money_change.status = 2
                    order_pickup_money_change.price = product_order.pickup_fee
                    order_pickup_money_change.order_no = product_order.order_no
                    order_pickup_money_change.custom_save()
                    
                    product_money_change = UserMoneyChange()
                    product_money_change.user = user
                    product_money_change.trade_type = 3
                    product_money_change.status = 2
                    product_money_change.price = product_order.product_price
                    product_money_change.order_no = product_order.order_no
                    product_money_change.custom_save()
                    
                    system_config = SystemConfig.objects.get(id=1)
                    platform_user = User.objects.get(username=system_config.platform_user)
                    
                    express_money_change = UserMoneyChange()
                    express_money_change.user = platform_user
                    express_money_change.trade_type = 18
                    express_money_change.status = 2
                    express_money_change.price = product_order.express_fee
                    express_money_change.order_no = product_order.order_no
                    express_money_change.custom_save()
                    pickup_money_change = UserMoneyChange()
                    pickup_money_change.user = platform_user
                    pickup_money_change.trade_type = 19
                    pickup_money_change.status = 2
                    pickup_money_change.price = product_order.pickup_fee
                    pickup_money_change.order_no = product_order.order_no
                    pickup_money_change.custom_save()
                    product_order.status = 2
                    product_order.pay_type = 1
                    product_order.effective = True
                    product_order.save()
                    order_result = order_success(product_order)
                    if order_result:
                        return render(request, 'basket/order_success.html','')
                else:
                    return render(request, 'basket/pay_order.html', ctx) 
        except:
            traceback.print_exc()
            return render(request, 'basket/order_error.html','')
            
            
@transaction.atomic
def order_success(product_order):
    all_info = product_order.order_info.all()
    for info in all_info:
        order_commission(info.product,product_order.user,info.price,info.product_num,info.product_num,1,product_order)        
    #生成提货单
    if product_order.pickup_addr:
        try:
            user_pickup_addr = UserPickupAddr.objects.get(user=product_order.user,pickup_addr=product_order.pickup_addr)
        except UserPickupAddr.DoesNotExist:
            user_pickup_addr = UserPickupAddr.objects.create(user=product_order.user,pickup_addr=product_order.pickup_addr)
        pickup_list = PickupList.objects.create(user=product_order.user, pickup_type=product_order.pickup_type, status=4,
                                                    user_address=product_order.receive_addr,user_picked_addr_id=user_pickup_addr.id,
                                                    pickup_fee=float(product_order.pickup_fee),
                                                    express_fee=float(product_order.express_fee))
    else:
        pickup_list = PickupList.objects.create(user=product_order.user, pickup_type=product_order.pickup_type, status=4,
                                                    user_address=product_order.receive_addr,
                                                    pickup_fee=float(product_order.pickup_fee),
                                                    express_fee=float(product_order.express_fee))
    pickup_list.custom_save()
    product_order.pickup_list = pickup_list
    product_order.save()
    #生成提货单详细
    if product_order.pickup_type == 1:
        pickup_detail_type = 1
    elif product_order.pickup_type == 2:
        pickup_detail_type = 3
    else:
        pickup_detail_type = 2
    user_address = pickup_list.user_address
    user_address_str = ''.join([user_address.province.name,
                                user_address.city.name,
                                user_address.district.name, user_address.address])
    consignee = user_address.consignee
    mobile_phone = user_address.mobile_phone
    for info in all_info:
        pickup_detail = PickupDetail.objects.create(pickup_list_id=pickup_list,product=info.product,quantity=info.product_num,
                                                 pickup_type=pickup_detail_type,pickup_captcha=pickup_list.pickup_captcha,
                                                 pickup_addr=pickup_list.user_picked_addr.pickup_addr if pickup_list.user_picked_addr else None,
                                                 user_address=user_address_str,status=4,
                                                 consignee=consignee, mobile_phone=mobile_phone)
        info.order_pickup_detail = pickup_detail
        info.save()
    return True

#取消订单
def order_cancel(request, pk):
    product_order = ProductOrder.objects.get(id=pk)
    product_order.effective = False
    product_order.save()
    return redirect('customer:order_manage')

