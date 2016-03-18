# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from oscar.core.loading import get_class
# from stars.apps.customer.safety.real_name_auth_views import RealNameAuthView

safety_center_view = get_class('customer.safety.views', 'SafetyCenterView')
update_password_view = get_class('customer.safety.views', 'UpdatePasswordView')
# valid_update_password_view = get_class('customer.safety.views', 'ValidUpdatePasswordView')

# verify_update_mail = get_class('customer.safety.views', 'VerifyUpdateMailView')
update_mail = get_class('customer.safety.views', 'UpdateMailView')
send_identity_valid_mail = get_class('customer.safety.views', 'SendIdentityValidMailView')
valid_identity_mail = get_class('customer.safety.views', 'ValidIdentityMailView')
send_bind_mail = get_class('customer.safety.views', 'SendBindMailView')
valid_bind_mail = get_class('customer.safety.views', 'ValidBindMailView')

#修改手机号
updateMobileView = get_class('customer.safety.views', 'UpdateMobileView')
sendMobileView = get_class('customer.safety.views', 'MobileVerificationCodeView')
bindMobileView = get_class('customer.safety.views', 'BindMobileView')
validBindMobileView = get_class('customer.safety.views', 'ValidBindMobileView')
#资金密码
updatePayPwdView = get_class('customer.safety.views', 'UpdatePayPwdView')
# validUpdatePayPwd = get_class('customer.safety.views', 'ValidUpdatePayPwdView')


urlpatterns = (
      url(r'^$',
        login_required(safety_center_view.as_view()),
        name='safety-center'),
    url(r'^center/$',
        login_required(safety_center_view.as_view()),
        name='safety-center'),
    url(r'^updatePassword/$',
        login_required(update_password_view.as_view()),
        name='safety-change_login_password'),
    # url(r'^validUpdatePassword/$',
    #     login_required(valid_update_password_view.as_view()),
    #     name='safety-valid_change_login_password'),

    # url(r'^validate/verify/mail/updateMail/$',
    #     login_required(verify_update_mail.as_view()),
    #     name='safety-validate-verify-mail-update_mail'),
    url(r'^validate/mail/updateMail/$',
        login_required(update_mail.as_view()),
        name='safety-validate-mail-update_mail'),
    url(r'^validate/mail/sendIdentityValidMail/$',
        login_required(send_identity_valid_mail.as_view()),
        name='safety-validate-mail-send_identity_valid_mail'),
    url(r'^validate/verify/validIdentityMail/$',
        login_required(valid_identity_mail.as_view()),
        name='safety-validate-verify-valid_identity_mail'),
    url(r'^validate/mail/sendBindMail/$',
        login_required(send_bind_mail.as_view()),
        name='safety-validate-mail-send_bind_mail'),
    url(r'^validate/mail/validBindMail/$',
        login_required(valid_bind_mail.as_view()),
        name='safety-validate-mail-valid_bind_mail'),


    url(r'^validate/mobile/updateMobile/$',
        login_required(updateMobileView.as_view()),
        name='safety-validate-mobile-update_mobile'),
    url(r'^validate/mobile/sendMobileCode/$',
        login_required(sendMobileView.as_view()),
        name='safety-validate-mobile-send_mobile_code'),
    url(r'^validate/mobile/bindMobile/$',
        login_required(bindMobileView.as_view()),
        name='safety-validate-mobile-bind_mobile'),
     url(r'^validate/mobile/bindMobile/$',
        login_required(validBindMobileView.as_view()),
        name='safety-validate-mobile-valid_bind_mobile'),

    url(r'^validate/payPwd/updatePayPwd/$',
        login_required(updatePayPwdView.as_view()),
        name='safety-validate-payment-update_password'),
    # url(r'^validate/payPwd/validUpdatePayPwd/$',
    #     login_required(validUpdatePayPwd.as_view()),
    #     name='safety-validate-payment-valid_update_password'),

    # 提货密码 # 删除 by lwj 20151026
    # url(r'^validate/updateDeliveryPwd/$',
    #     login_required(UpdateDeliveryPwdView.as_view()),
    #     name='safety-validate-delivery-update_password'),
    # url(r'^validate/deliveryPwd/validUpdateDeliveryPwd/$',
    #     login_required(ValidUpdateDeliveryPwdView.as_view()),
    #     name='safety-validate-delivery-valid_update_password'),
    # 实名认证 功能删除 by lwj 20151026
    # url(r'^realName/auth/$',
    #     login_required(RealNameAuthView.as_view()),
    #     name='safety-real_name_auth'),

)

