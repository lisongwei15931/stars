#coding=utf-8

from django.conf.urls import patterns,url

from .views import (userpickup_addr,userpickup_addr_add,userpickup_addr_update
                    ,userpickup_addr_del,userpickup_addr_default,get_pickupaddr)

urlpatterns = patterns('',
    url('^$',userpickup_addr,name = 'user_pickup'),
    #===========================================================================
    # 自提人员信息处理
    # url('^del_contact/(?P<contact_id>\d+)$',pickup_contact_del,name = 'del_contact'),
    # url('^add_contact/$',pickup_contact_add,name = 'add_contact'),
    # url('^update_contact/$',pickup_contact_update,name = 'update_contact'),
    #===========================================================================
    url('^del_pickup/(?P<pickup_id>\d+)$',userpickup_addr_del,name = 'del_pickup'),
    url('^default_pickup/(?P<pickup_id>\d+)$',userpickup_addr_default,name = 'default_pickup'),
    url('^add_pickup/$',userpickup_addr_add,name='add_pickup'),
    url('^update_pickup/(?P<pickup_id>\d+)$',userpickup_addr_update,name='update_pickup'),
    url('^get_pickupaddr/$',get_pickupaddr,name='get_pickupaddr'),
    
)