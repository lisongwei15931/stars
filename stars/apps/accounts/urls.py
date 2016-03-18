# encoding: utf-8


from django.conf.urls import patterns, url, include

urlpatterns = patterns('stars.apps.accounts.views',
    url(r'^check-mobile-phone/$', 'check_mobile_phone', name='check_mobile_phone'),
    url(r'^check-register-mobile-phone/$', 'check_register_mobile_phone', name='check_register_mobile_phone'),
    url(r'^check-username/$', 'check_username', name='check_username'),
    url(r'^check-introducer/$', 'check_introducer', name='check_introducer'),
    url(r'^register/$', 'register', name='register'),
    url(r'^send-captcha/$', 'send_captcha', name='send_captcha'),
    url(r'^user-agreement/$', 'user_agreement', name='user_agreement'),
    url(r'^set-identity/(?P<userprofile_id>\d+)/$', 'set_identity', name='set_identity'),
    url(r'^register-finish/(?P<user_id>\d+)/$', 'register_finish', name='register_finish'),
    url(r'^login/$', 'user_login', name='login'),
    url(r'^logout/$', 'user_logout', name='logout'),
    # url(r'^reset-password/$', 'reset_password', name='reset_password'),
    # url(r'^logout/$', 'user_logout', name='logout'),
    url(r'^forgetpw/$','forgetpw',name='forgetpw'),
    url(r'^resetpw/$','resetpw',name='resetpw'),
    url(r'^resetpw-finish/$','resetpw_finish',name = 'resetpw_finish'),
)
