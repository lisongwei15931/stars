# -*- coding: utf-8 -*-s

"""stars URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from oscar.app import application
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('stars.apps.accounts.urls', namespace='accounts')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'tradingcenter/', include('stars.apps.tradingcenter.urls', namespace='tradingcenter')),
    url(r'commission/', include('stars.apps.commission.urls', namespace='commission')),
    url(r'platform/', include('stars.apps.platform.urls', namespace='platform')),
    url(r'^helper/', include('stars.apps.helper.urls', namespace='helper')),
    url(r'^api/', include('stars.apps.api.urls', namespace='api')),
    url(r'^m/',include('stars.apps.mobile.urls',namespace='mobile')),
    url(r'', include(application.urls)),
]

# 部署时下面两个注释要解开
# urlpatterns += staticfiles_urlpatterns()
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 部署时下面4行要注释 （这个是本地测试404页面用的）
urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT },name='media'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.STATICFILES_DIRS[0] },name='static'),
)
