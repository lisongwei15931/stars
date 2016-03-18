# -*- coding: utf-8 -*-
import hashlib
import logging
import random
import string
from datetime import datetime

from django.contrib.auth.hashers import make_password, check_password
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from oscar.core.compat import get_user_model
from oscar.core.loading import (
     get_classes)
from stars.apps.accounts.models import UserProfile
from stars.apps.customer.safety.common_const import CommonEmailData
from stars.apps.customer.safety.models import MailVerificationCode, SmsVerificationCode
from stars.apps.public.send_message import send_message
from utils import mask_mail_url, mask_mobile, send_update_mail_confirmation, \
    send_updated_mail_notification,generate_sms_verification_code, \
    get_choice_value_list, check_pwd, is_valid_mail_addr

PageTitleMixin, = get_classes(
    'customer.mixins', ['PageTitleMixin', ])


User = get_user_model()


class SafetyCenterView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        rank = 1
        if user.email:
            email = mask_mail_url(user.email)
            rank += 1
        else:
            email = ''
        mobile = ''
        has_pay_pwd = False
        has_delivery_pwd = False
        if hasattr(user, 'userprofile'):
            if user.userprofile.mobile_phone:
                rank += 1
                mobile = mask_mobile(user.userprofile.mobile_phone)
            if user.userprofile.pay_pwd:
                has_pay_pwd = True
            if user.userprofile.pickup_pwd:
                has_delivery_pwd = True

        if has_pay_pwd:
            rank += 1
        if has_delivery_pwd:
            rank += 1

        payment_pwd = {'exist': has_pay_pwd,
                       # 'safe_rank': 3, 'tip': '建议设置更高强度密码',
                       }
        delivery_pwd = {'exist': has_delivery_pwd,
                       # 'safe_rank': 3, 'tip': '建议设置更高强度密码',
                       }
        safe_rank = {'rank': rank,
                     # 'text': '低',
                     # 'tip': '建议您启动全部安全设置，以保障账户及资金安全。'
                     }
        m = {'safe_rank': safe_rank, 'email': email, 'mobile': mobile, 'payment_pwd': payment_pwd, 'delivery_pwd': delivery_pwd}
        m['frame_id'] = 'safety'

        tpl = 'customer/safety/account_safety.html'
        return render(request, tpl, m)

    def has_pay_pwd(self):
        return UserProfile.objects.filter(user=self.request.user).exists()


class UpdatePasswordView(APIView):
    def get(self, request, *args, **kwargs):
        tpl = 'customer/safety/password/update_login_pwd.html'
        return render(request, tpl)

    def post(self, request, *args, **kwargs):
            user = request.user
            data = request.data

            old_pwd = data.get('old_pwd')
            new_pwd = data.get('new_pwd')

            (is_valid, msg) = check_pwd(new_pwd)
            if not is_valid:
                tpl = 'customer/safety/password/update_login_pwd_failed.html'
                return render(request, tpl, {'msg': msg})

            m = {}
            if user.check_password(old_pwd):
                # 进入修改成功页面
                tpl = 'customer/safety/password/update_login_pwd_suc.html'
                user.set_password(new_pwd)
                user.save(update_fields=['password'])

            else:
                # # 进入修改失败页面
                # tpl = 'customer/safety/password/update_login_pwd_failed.html'
                tpl = 'customer/safety/password/update_login_pwd.html'
                m['old_pwd_err_msg'] = u'原密码错误'

            return render(request, tpl, m)

# class ValidUpdatePasswordView(APIView):
#     def post(self, request, *args, **kwargs):
#         user = request.user
#         data = request.data
#
#         old_pwd = data.get('old_pwd')
#         new_pwd = data.get('new_pwd')
#
#         (is_valid, msg) = check_pwd(new_pwd)
#         if not is_valid:
#             tpl = 'customer/safety/password/update_login_pwd_failed.html'
#             return render(request, tpl, {'msg': msg})
#
#         m = {}
#         if user.check_password(old_pwd):
#             # 进入修改成功页面
#             tpl = 'customer/safety/password/update_login_pwd_suc.html'
#             user.set_password(new_pwd)
#             user.save(update_fields=['password'])
#
#         else:
#             # # 进入修改失败页面
#             # tpl = 'customer/safety/password/update_login_pwd_failed.html'
#             tpl = 'customer/safety/password/update_login_pwd.html'
#             m['old_pwd_err_msg'] = u"原密码错误"
#
#         return render(request, tpl, m)


class UpdatePayPwdView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

         # 进入修改页面
        if hasattr(user, 'userprofile') and user.userprofile.pay_pwd:
            tpl = 'customer/safety/paypwd/update_pay_pwd.html'
        else:
            tpl = 'customer/safety/paypwd/set_pay_pwd.html'

        return render(request, tpl)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        is_upd = 'old_pwd' in data
        old_pwd = data.get('old_pwd')
        new_pwd = data.get('new_pwd')

        (is_valid, msg) = check_pwd(new_pwd)
        if not is_valid:
            if old_pwd:
                tpl = 'customer/safety/paypwd/update_pay_pwd_failed.html'
            else:
                tpl = 'customer/safety/paypwd/set_pay_pwd_failed.html'
            return render(request, tpl, {'msg': msg})

        m = {}

        user_profile = UserProfile.objects.filter(user=user).last()
        failed = False
        tpl = ''
        if user_profile and user_profile.pay_pwd and not check_password(old_pwd, user_profile.pay_pwd):
            failed = True
            m['old_pwd_err_msg'] = u'原密码错误'
        elif user.check_password(new_pwd):
            failed = True
            m['new_pwd_err_msg'] = u'资金密码不能和登录密码相同'
        elif not user_profile:
            UserProfile(user=user, pay_pwd=make_password(new_pwd)).save()
            # 进入修改成功页面
            tpl = 'customer/safety/paypwd/set_pay_pwd_suc.html'
        elif not user_profile.pay_pwd:
            user_profile.pay_pwd = make_password(new_pwd)
            user_profile.save(update_fields=['pay_pwd', 'modified_date', 'modified_time'])
            tpl = 'customer/safety/paypwd/update_pay_pwd_suc.html'
        else:
            user_profile.pay_pwd = make_password(new_pwd)
            user_profile.save(update_fields=['pay_pwd', 'modified_date', 'modified_time'])
            tpl = 'customer/safety/paypwd/update_pay_pwd_suc.html'

        if failed:
            if is_upd:
                tpl = 'customer/safety/paypwd/update_pay_pwd.html'
            else:
                tpl = 'customer/safety/paypwd/set_pay_pwd.html'

        return render(request, tpl, m)

# class ValidUpdatePayPwdView(APIView):
#     def post(self, request, *args, **kwargs):
#         user = request.user
#         data = request.data
#
#         old_pwd = data.get('old_pwd')
#         new_pwd = data.get('new_pwd')
#
#         (is_valid, msg) = check_pwd(new_pwd)
#         if not is_valid:
#             if old_pwd:
#                 tpl = 'customer/safety/paypwd/update_pay_pwd_failed.html'
#             else:
#                 tpl = 'customer/safety/paypwd/set_pay_pwd_failed.html'
#             return render(request, tpl, {'msg': msg})
#
#         m = {}
#
#         user_profile = UserProfile.objects.filter(user=user).last()
#         if not user_profile:
#             UserProfile(user=user, pay_pwd=make_password(new_pwd)).save()
#             # 进入修改成功页面
#             tpl = 'customer/safety/paypwd/set_pay_pwd_suc.html'
#         elif not user_profile.pay_pwd:
#             user_profile.pay_pwd = make_password(new_pwd)
#             user_profile.save(update_fields=['pay_pwd', 'modified_date', 'modified_time'])
#             tpl = 'customer/safety/paypwd/update_pay_pwd_suc.html'
#         elif check_password(old_pwd, user_profile.pay_pwd):
#             user_profile.pay_pwd = make_password(new_pwd)
#             user_profile.save(update_fields=['pay_pwd', 'modified_date', 'modified_time'])
#             tpl = 'customer/safety/paypwd/update_pay_pwd_suc.html'
#         else:
#             # 进入修改失败页面
#             tpl = 'customer/safety/paypwd/update_pay_pwd_failed.html'
#             m['msg'] = u"原密码错误"
#
#         return render(request, tpl, m)


class UpdateMailView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        key = request.GET.get('r')

        m = {}
        if not user.email or self.__check_and_set_valid_action(user, key):
        # if True:
            # 进入修改页面
            if not user.email:
                tpl = 'customer/safety/email/bind_mail.html'
            else:
                m = {'current_mail': mask_mail_url(request.user.email)}
                tpl = 'customer/safety/email/update_mail.html'
        else:
            # 进入验证页面
            mail = mask_mail_url(request.user.email)
            m = {'current_mail': mail}
            tpl = 'customer/safety/email/update_old_mail.html'

        return render(request, tpl, m)

    @staticmethod
    def __check_and_set_valid_action(user, key):
        return MailVerificationCode.objects.filter(user=user, code=key, expired_time__gt=datetime.now(),
                                            status=0, type=2).update(status=1)

# class VerifyUpdateMailView(APIView):
#     #原邮箱验证
#     def get(self, request, *args, **kwargs):
#         mail = mask_mail_url(request.user.email)
#
#         m = {'mail': mail}
#         return Response(data=m)


class SendIdentityValidMailView(APIView):
    # 向原邮箱发送验证信息
    def get(self, request, *args, **kwargs):
        user = request.user
        mail = user.email

        key = self.__create_verify_key()
        MailVerificationCode(user=user, code=key, type=3,
                             expired_time=datetime.now()+CommonEmailData.UPDATE_MAIL_VERIFICATION_CODE_EXPIRED_TIME).save()
        m = {'link': self.__create_link(key, 'updateEmail'),
             'type': 'updateEmail',
             'new_mail': mail,
             }
        send_update_mail_confirmation(mail, m['link'])

        tpl = 'customer/safety/email/update_mail_msg.html'

        return render(request, tpl, m)
        # return Response(data=m)

    @classmethod
    def __create_verify_key(cls):
        return hashlib.md5(''.join(random.sample(string.ascii_lowercase+string.digits, 30))).hexdigest()

    @classmethod
    def __create_link(cls, key, event_type):
        url = reverse('customer:safety-validate-verify-valid_identity_mail')
        k = key
        return '{url}?k={k}&type={type}'.format(url=url,k=k,type=event_type)


class ValidIdentityMailView(APIView):
    #原邮箱验证
    def get(self, request, *args, **kwargs):
        user = request.user
        key = request.GET.get('k')
        event_type = request.GET.get('type')

        if self.check_and_set_valid_action(user, key):
            # 进入修改页面
            key = self.create_verify_key()
            MailVerificationCode(user=user, code=key, type=2,
                                 expired_time=datetime.now()+CommonEmailData.UPDATE_MAIL_VERIFICATION_CODE_EXPIRED_TIME).save()
            m = {'action_no': key,
                 'type': 'updateEmail',
                 'link': self.create_link(key, 'updateEmail',),
                 'current_mail': mask_mail_url(user.email),
                 }

            # return Response(data=m)
            tpl = 'customer/safety/email/update_mail.html'

            return render(request, tpl, m)
        else:
            # 进入验证错误页面
            m = {'msg': u'链接失效'}

            tpl = 'customer/safety/email/invalid_link.html'

            return render(request, tpl, m)

    @staticmethod
    def check_and_set_valid_action(user, key):
        return MailVerificationCode.objects.filter(user=user, code=key, expired_time__gt=datetime.now(),
                                            status=0, type=3).update(status=1)

    @staticmethod
    def create_verify_key():
        return hashlib.md5(''.join(random.sample(string.ascii_lowercase+string.digits, 30))).hexdigest()

    @classmethod
    def create_link(cls, key, event_type):
        url = reverse('customer:safety-validate-mail-send_bind_mail')
        k = key
        return '{url}?r={k}&type={type}'.format(url=url,k=k,type=event_type)


# class UpdateMailView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         key = request.GET.get('r')
#
#         if not user.email or self.is_valid_action(key):
#             # 进入修改页面
#             action_no = None
#             # pass
#         else:
#             # 进入验证页面
#             pass
#
#         m = {}
#         return Response(data=m)
#
#     def is_valid_action(self, key):
#         pass


class SendBindMailView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        data = request.GET
        key = data.get('action_no')
        # event_type = data.get('type')
        new_mail = str(data.get('new_mail')).lower()

        # if True:
        if is_valid_mail_addr(new_mail) and (not user.email or self.check_and_set_valid_action(user, key)):
            # 返回发送成功页面
            key = self.create_verify_key()
            MailVerificationCode(user=user, code=key, type=1, data=new_mail,
                                 expired_time=datetime.now()+CommonEmailData.UPDATE_MAIL_VERIFICATION_CODE_EXPIRED_TIME).save()
            m = {'action_no': key,
                 'type': 'updateEmail',
                 'link': self.create_link(key, 'updateEmail'),
                 'new_mail': new_mail}
            send_update_mail_confirmation(new_mail, m['link'])
            if user.email:
                tpl = 'customer/safety/email/bind_mail_msg.html'
            else:
                tpl = 'customer/safety/email/new_bind_mail_msg.html'

            return render(request, tpl, m)
        else:
            if not is_valid_mail_addr(new_mail):
                m = {'msg': u'邮箱地址不正确'}
            else:
                m = {'msg': u'链接失效'}

            tpl = 'customer/safety/email/invalid_link.html'

            return render(request, tpl, m)

    @staticmethod
    def check_and_set_valid_action(user, key):
        return MailVerificationCode.objects.filter(user=user, code=key, expired_time__gt=datetime.now(),
                                            status=0, type=2).update(status=1)

    @staticmethod
    def create_verify_key():
        return hashlib.md5(''.join(random.sample(string.ascii_lowercase+string.digits, 30))).hexdigest()

    @classmethod
    def create_link(cls, key, event_type):
        url = reverse('customer:safety-validate-mail-valid_bind_mail')
        k = key
        return '{url}?r={k}&type={type}'.format(url=url,k=k,type=event_type)


class ValidBindMailView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        key = request.GET.get('r')
        event_type = request.GET.get('type')

        data = self.__get_verification_code(user, key)
        if data:
            #修改邮箱
            new_email = data.data
            old_email = user.email
            try:
                with transaction.atomic():
                    data.status=1
                    data.comment = 'update mail from {} to {}'.format(old_email,new_email)
                    data.save(update_fields=['status', 'comment'])

                    user.email = new_email
                    user.save(update_fields=['email'])

            except Exception as e:
                logging.exception(e)
                return Response('更新错误.', status=500)
            else:
                #修改成功，向旧邮箱发送邮箱修改通知
                if old_email:
                    self.__notify_email(old_email, new_email)

                # 进入修改成功页面
                m = {'msg': u'修改成功'}
                tpl = 'customer/safety/email/bind_mail_suc.html'

                return render(request, tpl, m)
        else:
            # 进入验证错误页面
            m = {'msg': u'链接失效'}

            tpl = 'customer/safety/email/invalid_link.html'

            return render(request, tpl, m)

    @staticmethod
    def __notify_email(old_email, new_email):
        send_updated_mail_notification(old_email, new_email, datetime.now())

    @staticmethod
    def __get_verification_code(user, key):
        return MailVerificationCode.objects.filter(user=user, code=key, status=0, type=1).last()


class UpdateMobileView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        if False: #not hasattr(user, 'userprofile') or not user.userprofile.mobile_phone:
            # 当前没有绑定手机，进入绑定页面
            tpl = 'customer/safety/mobile/bind_mobile.html'
            # m = {"current_mobile": '12345678901'}
            return render(request, tpl)
        else:
            # 进入修改页面
            tpl = 'customer/safety/mobile/update_mobile.html'
            # m = {"current_mobile": mask_mobile(user.userprofile.mobile_phone)}
            m = {"current_mobile": mask_mobile(user.userprofile.mobile_phone)}
            return render(request, tpl, m)

    def post(self, request, *args, **kwargs):
        user = request.user
        vcode = request.data.get('vcode')

        flag = SmsVerificationCode.objects.filter(user=user, code=vcode,
                                         status=0, type=1, expired_time__gte=datetime.now()).exists()
        if flag:
            # 进入绑定页面
            tpl = 'customer/safety/mobile/bind_mobile.html'
            # m = {"current_mobile": '12345678901'}
            s = reverse('customer:safety-validate-mobile-bind_mobile')
            s += '?vcode='+vcode
            return HttpResponseRedirect(s)
            # return redirect('customer:safety-validate-mobile-bind_mobile', vcode=vcode)
        else:
            tpl = 'customer/safety/mobile/update_mobile.html'
            m = {"current_mobile": mask_mobile(user.userprofile.mobile_phone),
                 'msg': u'验证码无效',
                 'is_invalid_vcode':  True,
                 'vcode_err_msg': '验证码无效',
                 }
            return render(request, tpl, m)


class MobileVerificationCodeView(APIView):

    __UPDATE_MOBILE_TYPE = 1

    def get(self, request, *args, **kwargs):
        """
        验证码类型为修改手机号
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        data = request.GET

        try:
            code_type = int(request.GET.get('event'))
            if code_type not in get_choice_value_list(SmsVerificationCode.TYPE_CHOICES):
                return Response(status=http_status.HTTP_400_BAD_REQUEST)
            if code_type == 1:
                mobile = user.userprofile.mobile_phone
            elif code_type == 2:
                mobile = data['new_mobile']
                if UserProfile.objects.filter(mobile_phone=mobile).exclude(user=user).exists():
                    return JsonResponse(data={'msg': u'该手机号已经注册，不能绑定'}, status=http_status.HTTP_200_OK)
            else:
                raise ValueError
        except (ValueError, KeyError):
            return Response(status=http_status.HTTP_400_BAD_REQUEST)


        try:
            code = generate_sms_verification_code()
            SmsVerificationCode(user=user, code=code, type=code_type,data=mobile,
                                 expired_time=datetime.now()+CommonEmailData.SMS_VERIFICATION_CODE_EXPIRED_TIME).save()

            recipient = mobile
            send_content = u'您的验证码是：{code}。请不要把验证码泄露给其他人。'.format(code=code)

            (response_code, response_msg) = send_message(recipient, send_content)
            if response_code == '2':
                ret_status =http_status.HTTP_200_OK
            else:
                ret_status = http_status.HTTP_500_INTERNAL_SERVER_ERROR

            return JsonResponse(data={}, status=ret_status)

        except Exception as e:
            logging.exception(e)
            return JsonResponse(data={'msg': u'短信发送失败'}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


class BindMobileView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        vcode = request.GET.get('vcode')

        flag =1 #TODO
        # flag = SmsVerificationCode.objects.filter(user=user, code=vcode,
        #                                  status=0, type=1, expired_time__gte=datetime.now()).update(status=1)
        if flag>0:
            # 当前没有绑定手机，进入绑定页面
            tpl = 'customer/safety/mobile/bind_mobile.html'
            # m = {"current_mobile": '12345678901'}
            return render(request, tpl)
        else:
            tpl = 'customer/safety/mobile/update_mobile.html'
            m = {"current_mobile": mask_mobile(user.userprofile.mobile_phone),
                 'msg': u'验证码无效',
                 'is_invalid_vcode':  True,
                 'vcode_err_msg': u'验证码无效',
                 }
            return render(request, tpl, m)
            # return redirect('customer:safety-validate-mobile-update_mobile')
            # return redirect(reverse('customer:safety-validate-mobile-update_mobile'))

    def post(self, request, *args, **kwargs):
        user = request.user
        new_mobile = request.data['new_mobile']
        old_mobile = user.userprofile.mobile_phone if hasattr(user, 'userprofile') else ''

        vcode = request.data.get('vcode')

        verify_code_row = SmsVerificationCode.objects.filter(user=user, code=vcode,data=new_mobile,
                                             status=0, type=2, expired_time__gte=datetime.now()).last()
        if verify_code_row:
            # 修改手机号
            try:
                with transaction.atomic():
                    verify_code_row.status=1
                    verify_code_row.comment = 'update mobile from {} to {}'.format(old_mobile, new_mobile)
                    verify_code_row.save(update_fields=['status', 'comment'])

                    if hasattr(user, 'userprofile'):
                        user.userprofile.mobile_phone = new_mobile
                        user.userprofile.save(update_fields=['mobile_phone', 'modified_date', 'modified_time'])
                    else:
                        UserProfile.objects.create(user=user, mobile_phone=new_mobile)

            except Exception as e:
                logging.exception(e)
                return Response('更新错误.', status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # 修改成功，向旧手机发送修改通知
                self.__send_sms(old_mobile, new_mobile)

                # 进入修改成功页面
                m = {'msg': u'修改成功'}

                tpl = 'customer/safety/mobile/update_mobile_suc.html'
                # m = {"current_mobile": '12345678901'}
                return render(request, tpl)

        else:
            # 验证错误
            tpl = 'customer/safety/mobile/bind_mobile.html'
            m = {'msg': u'验证失败',
                 'is_invalid_vcode':  True,
                 'vcode_err_msg': u'验证码无效',
                 'new_mobile': new_mobile,
                 # 'vcode': vcode,
                 }

            return render(request, tpl, m)

    @staticmethod
    def __send_sms(old, new):
        # TODO
        pass


class ValidBindMobileView(APIView):

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        new_mobile = data['new_mobile']
        old_mobile = user.userprofile.mobile_phone if hasattr(user, 'userprofile') else ''

        vcode = data['vcode']

        verify_code_row = SmsVerificationCode.objects.filter(user=user, code=vcode,
                                             status=0, type=1).last()
        if verify_code_row:
            # 修改手机号
            try:
                with transaction.atomic():
                    verify_code_row.status=1
                    verify_code_row.comment = 'update mail from {} to {}'.format(old_mobile, new_mobile)
                    verify_code_row.save(update_fields=['status', 'comment'])

                    if hasattr(user, 'userprofile'):
                        user.userprofile.mobile_phone = new_mobile
                        user.userprofile.save(update_fields=['mobile_phone'])
                    else:
                        UserProfile.objects.create(user=user, mobile_phone=new_mobile)

            except Exception as e:
                logging.exception(e)
                # return Response(e, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response(u'更新错误.', status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # 修改成功，向旧手机发送修改通知
                self.__send_sms(old_mobile, new_mobile)

                # 进入修改成功页面
                m = {'msg': u'修改成功'}

                return Response(data=m)

        else:
            # 进入验证错误页面
            m = {'msg': u'验证失败',
                 'is_invalid_vcode': True,
                 'vcode_err_msg': u'验证码无效'}

            return Response(data=m)

    @staticmethod
    def __send_sms(old, new):
        # TODO
        pass

# 提货密码功能删除 by lwj 20151026
# class UpdateDeliveryPwdView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user
#
#          # 进入修改页面
#         if hasattr(user, 'userprofile') and user.userprofile.pickup_pwd:
#             tpl = 'customer/safety/delivery_pwd/update_delivery_pwd.html'
#         else:
#             tpl = 'customer/safety/delivery_pwd/set_delivery_pwd.html'
#
#         return render(request, tpl)
#
#
# class ValidUpdateDeliveryPwdView(APIView):
#     def post(self, request, *args, **kwargs):
#         user = request.user
#         data = request.data
#
#         old_pwd = data.get('old_pwd')
#         new_pwd = data.get('new_pwd')
#
#         (is_valid, msg) = check_pwd(new_pwd)
#         if not is_valid:
#             if old_pwd:
#                 tpl = 'customer/safety/delivery_pwd/update_delivery_pwd_failed.html'
#             else:
#                 tpl = 'customer/safety/delivery_pwd/set_pay_delivery_pwd_failed.html'
#             return render(request, tpl, {'msg': msg})
#
#         m = {}
#
#         user_profile = UserProfile.objects.filter(user=user).last()
#         if not user_profile:
#             UserProfile(user=user, pay_pwd=make_password(new_pwd)).save()
#             # 进入设置成功页面
#             tpl = 'customer/safety/delivery/set_delivery_pwd_suc.html'
#         elif not user_profile.pickup_pwd:
#             # 进入设置成功页面
#             user_profile.pickup_pwd = make_password(new_pwd)
#             user_profile.save(update_fields=['pickup_pwd', 'modified_date', 'modified_time'])
#             tpl = 'customer/safety/delivery_pwd/set_delivery_pwd_suc.html'
#         elif check_password(old_pwd, user_profile.pickup_pwd):
#             user_profile.pickup_pwd = make_password(new_pwd)
#             # user_profile.save()
#             user_profile.save(update_fields=['pickup_pwd', 'modified_date', 'modified_time'])
#             tpl = 'customer/safety/delivery_pwd/update_delivery_pwd_suc.html'
#         else:
#             # 进入修改失败页面
#             tpl = 'customer/safety/delivery_pwd/update_delivery_pwd_failed.html'
#             m['msg'] = u"原密码错误"
#
#         return render(request, tpl, m)