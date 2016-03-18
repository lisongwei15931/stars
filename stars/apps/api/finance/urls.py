# coding=utf-8
from django.conf.urls import patterns, url, include

import ab.urls
import wx.urls
import ali.urls

urlpatterns = patterns('',
    url(r'^ab/', include(ab.urls)),
    url(r'^wx/', include(wx.urls)),
    url(r'^ali/', include(ali.urls)),
)

