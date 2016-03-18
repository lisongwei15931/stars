#coding=utf-8

from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from stars.apps.commission.models import UserPickupAddr,PickupAddr
from .forms import UserPickupForm
from stars.apps.address.models import(Province, City, District)
import json
from django.template.loader import get_template
from django.template import Context



@login_required
def userpickup_addr(request):
    user = request.user
    try :
        userpickup_addr = UserPickupAddr.objects.filter(user=user).order_by('-is_default','-created_datetime')
        #pickup_contact = UserPickupContact.objects.filter(user=user).first()
    except UserPickupAddr.DoesNotExist:
        pass
    context = {'userpickup_addr':userpickup_addr,'frame_id':'user_pickup'}
    
    return render(request,'customer/userpickup/userpickup_addr.html',context)

@login_required 
def userpickup_addr_add(request):
    user = request.user 
    form = UserPickupForm()
    
    userpickup_addr = UserPickupAddr.objects.filter(user=user)
    #用户已有自提点
    exclude_userpickup_addr_ids = userpickup_addr.values_list('pickup_addr')
    
    #用户可选地址
    pickup_address_list = PickupAddr.objects.exclude(id__in = exclude_userpickup_addr_ids)
    #返回可选省list
    province_ids = pickup_address_list.values_list('province',flat = True )
    province_list = Province.objects.filter(id__in = province_ids)
    city_list = []
    
    
    if request.method == 'POST':
        form = UserPickupForm(request.POST)
        if form.is_valid():
            new_addr = form.save(commit = False)
            new_addr.user = user
            new_addr.save()
            
            return redirect('customer:user_pickup')
        
    context = {'pickup_address_list' : pickup_address_list,
               'province_list':province_list,
               'city_list' :city_list,
               'current_province_id':'all',
               'current_city_id':'all',
               'form':form ,
               'addr_add':True,
               }
        
    return render(request,'customer/userpickup/userpickup_addr_update.html',context)

@login_required 
def userpickup_addr_update(request,pickup_id):
    #pickup_id = request.GET.get('pickup_id','')
    user = request.user 
    try :
        userpickup_addr = UserPickupAddr.objects.filter(user=user)
        #用户已有自提点
        exclude_userpickup_addr_ids = userpickup_addr.values_list('pickup_addr')
    
        #用户可选地址
        pickup_address_list = PickupAddr.objects.exclude(id__in = exclude_userpickup_addr_ids)
        #返回可选省list
        province_ids = pickup_address_list.values_list('province',flat = True )
        province_list = Province.objects.filter(id__in = province_ids)
        city_list = []
        
        current_pickup_addr = UserPickupAddr.objects.get(id = pickup_id)
        pickup_address = PickupAddr.objects.filter(pk = current_pickup_addr.pickup_addr_id)
        current_province_id = pickup_address[0].province_id
        current_province = Province.objects.get(pk = current_province_id)
        current_city_id = pickup_address[0].city_id
        current_city = City.objects.get(pk=current_city_id)
    except:
        return redirect('customer:user_pickup')

    form = UserPickupForm(instance = current_pickup_addr )
    
    
    if request.method =='POST':
        form = UserPickupForm(request.POST,instance = current_pickup_addr)
        
        if form.is_valid():
            new_addr = form.save(commit = False )
            new_addr.user = user
            new_addr.save()
            
            return redirect('customer:user_pickup')
    
    context = {'pickup_address_list' : pickup_address,
               'province_list':province_list,
               'city_list' :city_list,
               'current_province':current_province,
               'current_city':current_city,
               'form':form ,
               'pickup_address':pickup_address ,
               'addr_upd':True ,
               }

    return render(request,'customer/userpickup/userpickup_addr_update.html',context)
    
    
    
    
    

@login_required 
def userpickup_addr_del(request,pickup_id):
    try:
        userpickup_addr = UserPickupAddr.objects.get(pk=pickup_id)
        userpickup_addr.delete()
    except :
        pass
    return redirect('customer:user_pickup')


@login_required 
def userpickup_addr_default(request,pickup_id):
    try:
        default_addr = UserPickupAddr.objects.filter(is_default=True).exclude(id=pickup_id)
    except:
        pass
    if default_addr :
        default_addr.update(is_default=False)
    try:
        new_default_addr = UserPickupAddr.objects.get(id=pickup_id)
        new_default_addr.is_default = True
        new_default_addr.save()
    except UserPickupAddr.DoesNotExist:
        return redirect('customer:user_pickup')   
    return redirect('customer:user_pickup')



def get_pickupaddr2(request):

    province_id = request.GET.get('province_id', '')
    city_id = request.GET.get('city_id', '')
    district_id = request.GET.get('district_id','')
    result = {}
    if province_id:
        try:
            current_province = Province.objects.get(id=province_id)

            exit_citys = PickupAddr.objects.values('city').filter(province_id = current_province).distinct()
            
            citys = City.objects.filter(id__in = exit_citys)
            citys_data = list(citys.values('id', 'name'))

            districts = District.objects.filter(city_id__in = exit_citys)
            districts_data = list(districts.values('id', 'name'))
            
            pickupaddrs = PickupAddr.objects.filter(province_id = province_id)
            pickupaddr_data = list(pickupaddrs.values('id','name'))

   
            result = {'citys': citys_data,'districts':districts_data,'pickupaddrs':pickupaddr_data}
        except:
            result = {'citys': [], 'districts': []}
    else :
        exist_provinces = PickupAddr.objects.values('province').distinct()
        provinces = Province.objects.filter(id__in=exist_provinces)
        province_data = list(provinces.values('id','name'))
        
        result = {'provinces':province_data}
    
    if city_id:
        try:
            current_city = City.objects.get(id=city_id)
            
            exit_districts = PickupAddr.objects.values('district').filter(city_id = current_city).distinct()
            
            districts = District.objects.filter(id__in = exit_districts)
            districts_data = list(districts.values('id', 'name'))
            
            pickupaddrs = PickupAddr.objects.filter(city_id = city_id)
            pickupaddr_data = list(pickupaddrs.values('id','name'))

            result = {'districts': districts_data,'pickupaddrs':pickupaddr_data}
        except:
            result = {'districts': []}
            
    if district_id :
        try :
            pickupaddrs = PickupAddr.objects.filter(district_id = district_id)
            pickupaddr_data = list(pickupaddrs.values('id','name'))
            
            result = {'pickupaddrs':pickupaddr_data}
        except :
            pass   
            
            
            
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


@login_required 
def get_pickupaddr(request):
    user = request.user 
    
    userpickup_addr = UserPickupAddr.objects.filter(user=user)
    #用户已有自提点
    exclude_userpickup_addr_ids = userpickup_addr.values_list('pickup_addr')
    
    #用户可选地址
    pickup_address_list = PickupAddr.objects.exclude(id__in = exclude_userpickup_addr_ids)
    #返回可选省list
    province_ids = pickup_address_list.values_list('province',flat = True )
    province_list = Province.objects.filter(id__in = province_ids)
    city_list = []
    
    #选取省市ajax
    if request.is_ajax() :
        province_id = request.GET.get('province_id','')
        city_id = request.GET.get('city_id','')
        
        if province_id and (not city_id):
            if province_id != 'all':
                try :
                    current_province = Province.objects.get(id = province_id)
                    pickup_address_list = PickupAddr.objects.filter(province=current_province).exclude(id__in=exclude_userpickup_addr_ids)
                    city_ids = pickup_address_list.values_list('city', flat=True)
                    city_list = City.objects.filter(id__in=city_ids)
                    current_template = get_template('customer/userpickup/userpickup_addr_content.html')
                    
                    context = {'pickup_address_list': pickup_address_list,
                            'province_list': province_list,
                            'city_list': city_list,
                            'current_province_id': current_province.id,
                            'current_city_id': 'all',
                            
                            }
                    
                    content_html = current_template.render(Context(context))
                    payload = {'content_html': content_html, 'success': True}
                    return HttpResponse(json.dumps(payload), content_type="application/json")
                    
                except :
                    pass
            else :
                pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_userpickup_addr_ids)

                province_ids = pickup_address_list.values_list('province', flat=True)
                province_list = Province.objects.filter(id__in=province_ids)
                city_list = []
                current_template = get_template('customer/userpickup/userpickup_addr_content.html')
                context = {'pickup_address_list': pickup_address_list,
                        'province_list': province_list,
                        'city_list': city_list,
                        'current_province_id': 'all',
                        'current_city_id': 'all',
                        }
                content_html = current_template.render(Context(context))
                payload = {'content_html': content_html, 'success': True}
                return HttpResponse(json.dumps(payload), content_type="application/json")
                    
        if city_id :
            if city_id !='all' :
                try:
                    all_pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_userpickup_addr_ids)
                    all_province_ids = all_pickup_address_list.values_list('province', flat=True)
                    province_list = Province.objects.filter(id__in=all_province_ids)

                    current_city = City.objects.get(id=city_id)
                    current_province = current_city.province
                    pickup_address_list = PickupAddr.objects.filter(city=current_city).exclude(id__in=exclude_userpickup_addr_ids)

                    city_ids = all_pickup_address_list.filter(province=current_province).values_list('city', flat=True)
                    city_list = City.objects.filter(id__in=city_ids)
                except:
                    pass
                
                current_template = get_template('customer/userpickup/userpickup_addr_content.html')
                context = {'pickup_address_list': pickup_address_list,
                        'province_list': province_list,
                        'city_list': city_list,
                        'current_province_id': current_province.id,
                        'current_city_id': current_city.id ,
                        }
                content_html = current_template.render(Context(context))
                payload = {'content_html': content_html, 'success': True}
                return HttpResponse(json.dumps(payload), content_type="application/json")
                    
            else :
                all_pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_userpickup_addr_ids)
                all_province_ids = all_pickup_address_list.values_list('province', flat=True)
                province_list = Province.objects.filter(id__in=all_province_ids)

                current_province = Province.objects.get(id=province_id)
                pickup_address_list = PickupAddr.objects.filter(province=current_province).exclude(id__in=exclude_userpickup_addr_ids)
                city_ids = pickup_address_list.values_list('city', flat=True)
                city_list = City.objects.filter(id__in=city_ids)
                
                current_template = get_template('customer/userpickup/userpickup_addr_content.html')
                context = {'pickup_address_list': pickup_address_list,
                        'province_list': province_list,
                        'city_list': city_list,
                        'current_province_id': current_province.id,
                        'current_city_id': 'all',
                        }
            
                content_html = current_template.render(Context(context))
                payload = {'content_html': content_html, 'success': True}
                return HttpResponse(json.dumps(payload), content_type="application/json")
    

    
#===============================================================================
#     
# ###自提人员信息处理
# 
# @login_required 
# def pickup_contact_del(request,contact_id):
#     try :
#         del_contact = UserPickupContact.objects.get(id = contact_id)
#         del_contact.delete()
#     except UserPickupContact.DoesNotExist :
#         return redirect('customer:user_pickup')
#     return redirect('customer:user_pickup')
# 
# @login_required 
# def pickup_contact_add(request):
#     user = request.user
#     form = UserPickupContactForm()
#     
#     if request.method == 'POST' :
#         form = UserPickupContactForm(request.POST)
#         
#         if form.is_valid():
#             new_contact = form.save(commit=False)
#             new_contact.user = user
#             new_contact.save()
#             
#             return redirect('customer:user_pickup')
#     
#     context = {'form':form,'add_contact':True}
#     
#     return render(request,'customer/userpickup/pickup_contact_add.html',context)
#     
# 
# @login_required 
# def pickup_contact_update(request):
#     user = request.user 
#     try :
#         contact = UserPickupContact.objects.get(user=user)
#     except UserPickupContact.DoesNotExist:
#         return redirect('customer:user_pickup')
#     form = UserPickupContactForm(instance=contact)
#     
#     if request.method == 'POST':
#         form = UserPickupContactForm(request.POST,instance = contact)
#         if form.is_valid():
#             new_contact = form.save(commit=False)
#             new_contact.user = user
#             new_contact.save()
#             
#             return redirect('customer:user_pickup')
#     
#     context = {'form':form}
#     return render(request,'customer/userpickup/pickup_contact_add.html',context)
#                
#===============================================================================
    
    
     
    

