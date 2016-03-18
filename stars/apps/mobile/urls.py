#coding=utf-8

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('stars.apps.mobile.views',
    url(r'^$', 'home_test', name='mobile_home'),
    url(r'^home/$', 'home_test', name='mobile_home'),
    url(r'^home_test/$', 'home_test', name='mobile_home_test'),
)

