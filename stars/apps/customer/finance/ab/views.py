# -*- coding: utf-8 -*-
import logging
from datetime import *

import re

from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from rest_framework import status as http_status
from rest_framework.views import APIView

from stars.apps.accounts.models import UserProfile
from stars.apps.commission.models import UserBank, UserBalance, UserMoneyChange
from stars.apps.customer.assets.utils import mask_bank_card_no, mask_id_card_no
from stars.apps.customer.finance.ab import ab_util
from stars.apps.customer.finance.ab.common_const import AgriculturalBankTradeConstData
from stars.apps.customer.finance.ab.service.ab_client_service import MarketSignContractService, RescindContractService, \
    RechargeService, WithdrawService, AccountBalanceQueryService
from stars.apps.customer.finance.ab.utils import is_none_or_empty_or_blank, is_none_or_empty
from stars.apps.customer.finance.common_const import ResultCode
from stars.apps.customer.finance.finance_exception import FinanceException, FinanceSysException, FinanceTradeException
from stars.apps.customer.finance.models import AbSignInContractLog, AbRescindContractLog, AbRechargeWithdrawLog
from stars.apps.customer.safety.common_const import CommonEmailData
from stars.apps.customer.safety.models import SmsVerificationCode
from stars.apps.customer.safety.utils import is_valid_id_card_num, generate_sms_verification_code
from stars.apps.customer.user_info.utils import get_user_inst_fund_acc_id
from stars.apps.public.send_message import send_message
from stars.apps.customer.finance.utils import need_market_opening


class AbSignInOutContractHomeView(APIView):
    __frame_id = 'ab_sign_in_out'

    __optional_items = {'gender', 'tel_no', 'fax_no', 'mobile', 'post_code', 'address', 'email'}

    @staticmethod
    def get_inst_fund_acc_id(user):
        return str(get_user_inst_fund_acc_id(user))

    @need_market_opening
    def get(self, request, *args, **kwargs):
        user = request.user
        ctx = {}
        ctx['frame_id'] = self.__class__.__frame_id

        if UserBank.objects.filter(user=user, is_rescinded=False, bank_name=u'中国农业银行').exists():
            ctx['username'] = user.username
            ctx['inst_fund_acc'] = AbSignInOutContractHomeView.get_inst_fund_acc_id(user)

            r = AbSignInContractLog.objects.filter(user=user, status=1).order_by('modified_time').last()
            if r:
                item_names = ['client_name', 'cert_id', 'fax_no', 'mobile', 'tel_no', 'postcode', 'address', 'email']
                for ele in item_names:
                    if hasattr(r, ele):
                        ctx[ele] = getattr(r, ele, '')
                ctx['bank_account'] = mask_bank_card_no(r.bank_account)
                ctx['cert_id'] = mask_id_card_no(r.cert_id)

            tpl = 'customer/finance/ab/rescind/step1.html'

        elif hasattr(user, 'userprofile') and user.userprofile.pay_pwd:
            ctx['user_name'] = user.username
            ctx['inst_fund_acc'] = self.get_inst_fund_acc_id(user)
            if user.userprofile.audit_status == 2:
                ctx['is_real_name_authed'] = True
                ctx['cert_id'] = mask_id_card_no(user.userprofile.identification_card_number)
                ctx['bank_account_name'] = user.userprofile.real_name
                ctx['cert_type'] = user.userprofile.cert_type
            tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_1.html'

        else:  # 需要先设置资金密码
            tpl = 'customer/finance/ab/sign_in/ab_sign_in_no_pwd.html'
            # return redirect('customer:safety-validate-payment-update_password')

        return render(request, tpl, ctx)


class AbSignInContractView(APIView):
    __frame_id = 'ab_sign_in_out'

    __optional_items = {'gender', 'tel_no', 'fax_no', 'mobile', 'post_code', 'address', 'email'}

    @classmethod
    def get_inst_fund_acc_id(cls, user):
        return str(get_user_inst_fund_acc_id(user))

    @need_market_opening
    def get(self, request, *args, **kwargs):
        return redirect('customer:finance-ab-sign_in_out_home')

    @need_market_opening
    def post(self, request, *args, **kwargs):
        user = request.user
        ret = self.do_sign_event(request, user)

        if ret['code'] == ResultCode.SUCCESS:
            tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_suc.html'
        elif ret['code'] == ResultCode.ERROR_PARAM:
            tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_1.html'
        else:
            tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_failed.html'
        return render(request, tpl, ret.get('data', {}))

    @classmethod
    def do_sign_event(cls, request, user):
        if UserBank.objects.filter(user=user, is_rescinded=False, bank_name=u'中国农业银行').exists():
            # tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_suc.html'
            return {'code': ResultCode.SUCCESS, 'msg': '', 'data': {}, }
            # return render(request, tpl, {})
        elif UserBank.objects.filter(bank_account=request.data.get('bank_account_no', ''),
                                     is_rescinded=False,
                                     bank_name=u'中国农业银行').exclude(user=user).exists():
            data = {'msgs': [u'该银行账户已经被其他用户签约']}
            # tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_failed.html'
            return {'code': ResultCode.BE_USED, 'msg': u'该银行账户已经被其他用户签约', 'data': data, }
            # return render(request, tpl, data)
        else:
            return cls.to_sign_in(request)

    @classmethod
    def to_sign_in(cls, request, is_json_format=False):
        user = request.user
        post_data = request.data

        data = {e[0]: e[1] for e in post_data.items()}
        data['frame_id'] = cls.__class__.__frame_id
        data['user_name'] = user.username
        data['inst_fund_acc'] = cls.get_inst_fund_acc_id(user)

        sign_in_data = {}
        ret = {'code': 0, 'msg': '', 'data': data, }
        try:
            sign_in_data['bank_account'] = data['bank_account_no']
            if data['account_type'] == '0' or not data['account_type'] or data['account_type'].startswith('0'):  # 个人
                is_business_account = False
                sign_in_data['bank_password'] = data['bank_account_pwd'].encode('utf8')
                sign_in_data['cert_type'] = '110001'
                check_flag = 1
            else:   # 公司
                is_business_account = True
                sign_in_data['trade_password'] = data['bank_account_pwd'].encode('utf8')
                sign_in_data['have_pwd'] = '1'
                sign_in_data['cert_type'] = '610001'
                check_flag = 2

            if user.userprofile.audit_status == 2:
                data['bank_account_name'] = user.userprofile.real_name
                data['cert_id'] = user.userprofile.identification_card_number
                data['cert_type'] = user.userprofile.cert_type
                check_flag = 0
        except (KeyError, ValueError):
            flag = 1
        else:
            flag = cls.check_input_data(data, check_flag)

        if flag != 0:  # error
            ret['code'] = ResultCode.ERROR_PARAM

            data['bank_account_pwd'] = ''
            if user.userprofile.audit_status == 2:
                data['cert_id'] = mask_id_card_no(user.userprofile.identification_card_number)

            return ret

        sign_in_data['inst_fund_acc'] = data['inst_fund_acc']
        sign_in_data['inst_branch'] = AgriculturalBankTradeConstData.DEFAULT_INST_BRANCH
        sign_in_data['transfer_limit'] = '0'
        sign_in_data['client_name'] = data['bank_account_name']
        sign_in_data['cert_id'] = data['cert_id']
        sign_in_data['inst_serial'] = MarketSignContractService.create_ab_inst_serial()
        # sign_in_data['client_kind'] = 0  # 0，个人；1：机构
        for item in cls.__class__.__optional_items:
            sign_in_data[item] = data.get(item, '')
        d = cls.log_to_db(user, sign_in_data)
        try:
            r = MarketSignContractService().do_event(data=sign_in_data)

            resp = r['data']
            d.code = resp['code']
            d.info = resp['info']
            d.client_no = resp['client_no']
            d.serial_no = resp['serial_no']
            d.summary = resp['summary']

            if r['status']['code'] == 0:  # 成功

                d.status = 1
                UserBank(user=user, bank_name=u'中国农业银行',
                         bank_account=d.bank_account, tel=d.tel_no,
                         client_no=d.client_no, client_name=d.client_name,
                         is_enable=True, is_business_account=is_business_account).save()
                user_profile = UserProfile.objects.get(user=user)
                if not user_profile.identification_card_number:
                    user_profile.identification_card_number = sign_in_data['cert_id']
                if not user_profile.real_name:
                    user_profile.real_name = sign_in_data['client_name']
                user_profile.cert_type = 0 if sign_in_data['cert_type'] == '110001' else 1
                user_profile.audit_status = 2
                user_profile.save()

                request._request.method = "GET"
                ret['code'] = ResultCode.SUCCESS
                # tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_suc.html'

            else:
                ret['code'] = ResultCode.FIN_RETURN_ERROR
                ret['msg'] = resp.get('info', '')
                # tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_failed.html'
                #5010 出入金关系已经存在
                if r['status']['code'] == '5010':
                    if resp['inst_fund_acc'] != sign_in_data['inst_fund_acc'] or UserBank.objects.filter(bank_account=sign_in_data['bank_account'], is_rescinded=False, bank_name=u'中国农业银行').exists():
                        data['msgs'] = [u'该银行账户已经被其他用户签约']
                        ret['code'] = data['msgs']
                    else:
                        bank_pwd = sign_in_data['bank_password'] if sign_in_data['bank_password'] else sign_in_data['trade_password']
                        query_data = {'client_no': d.client_no, 'bank_account': sign_in_data['bank_account'],
                                      'inst_fund_acc': sign_in_data['inst_fund_acc'],
                                      'bank_password': bank_pwd}
                        r2 = AccountBalanceQueryService().do_event(data=query_data)
                        if r['status']['code'] == 0 and not UserBank.objects.filter(user=user, is_rescinded=False, bank_name=u'中国农业银行').exists():

                            UserBank(user=user, bank_name=u'中国农业银行',
                                     bank_account=d.bank_account, tel=d.tel_no,
                                     client_no=d.client_no, client_name=d.client_name,
                                     is_enable=True, is_business_account=is_business_account).save()
                            ret['code'] = ResultCode.SUCCESS
                            # tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_suc.html'

                d.status = 2
                d.sys_comment = r['data']
                data['msgs'] = [r['status']['msg']]

            d.save()

            return ret
        except Exception as e:
            logging.exception(e)
            d.status = 2
            d.sys_comment = e
            d.save()

            ret['code'] = ResultCode.NET_ERROR

            data = {'msgs': [u'网络异常']}
            # tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_failed.html'
            # return render(request, tpl, data)
            return ret

    @classmethod
    def log_to_db(cls, user, data):
        d = AbSignInContractLog()
        d.user = user
        d.status = 3

        d.trade_date = datetime.now().date()
        d.trade_time = datetime.now().time()
        d.inst_serial = data['inst_serial']

        d.bank_account = data['bank_account']
        d.inst_func_acc = data['inst_fund_acc']
        d.client_name = data['client_name']
        d.cert_id = data['cert_id']
        d.cert_type = data['cert_type']
        d.trade_branch = data.get('trade_branch', '')

        d.user_comment = data.get('comment', '')
        d.tel_no = data.get('tel_no', '')
        d.save()

        return d

    __cannot_be_empty = u'不能为空'
    __must_be_digit = u'必须是数字'
    __invalid_length = u'长度不正确'

    @classmethod
    def check_input_data(cls, data, check_flag):
        flag = 0
        for item in data.items():
            if item[0].endswith('_msg'):
                item[1] = ''

        if is_none_or_empty_or_blank(data.get('bank_account_name')):
            data['bank_account_name_msg'] = cls.__cannot_be_empty
            flag = 1

        if is_none_or_empty_or_blank(data.get('bank_account_no')):
            data['bank_account_no_msg'] = cls.__cannot_be_empty
            flag = 1
        else:
            bank_account_no = data['bank_account_no'].replace(' ', '')
            if not bank_account_no.isdigit():
                data['bank_account_no_msg'] = cls.__must_be_digit
                flag = 1
            elif len(bank_account_no) < 15 or len(bank_account_no) > 22:
                data['bank_account_no_msg'] = cls.__invalid_length
                flag = 1

        if is_none_or_empty(data.get('bank_account_pwd')):
            data['bank_account_pwd_msg'] = cls.__cannot_be_empty
            flag = 1
        else:
            if not data['bank_account_pwd'].isdigit():
                data['bank_account_pwd_msg'] = cls.__must_be_digit
                flag = 1
            elif len(data['bank_account_pwd']) != 6:
                data['bank_account_pwd_msg'] = cls.__invalid_length
                flag = 1

        if check_flag != 0:
            if is_none_or_empty_or_blank(data.get('cert_id')):
                data['cert_id_msg'] = cls.__cannot_be_empty
                flag = 1
            elif check_flag == 1:  # 身份证
                cert_id = data['cert_id'].replace(' ', '')
                if not is_valid_id_card_num(cert_id):
                    data['cert_id_msg'] = u'证件号无效'
                    flag = 1
            else:  # 组织机构号码
                cert_id = data['cert_id'].replace(' ', '')
                if not re.compile('[0-9]+$').match(cert_id):
                    data['cert_id_msg'] = u'证件号无效'
                    flag = 1
        return flag


class AbRescindContractView(APIView):
    __frame_id = 'ab_sign_in_out'

    @need_market_opening
    def get(self, request, *args, **kwargs):
        user = request.user
        ctx = {}
        ctx['frame_id'] = self.__class__.__frame_id

        if UserBank.objects.filter(user=user, is_rescinded=False, bank_name=u'中国农业银行').exists():
            r = AbSignInContractLog.objects.filter(user=user, status=1).order_by('modified_time').last()

            if r:
                ctx['bank_account'] = mask_bank_card_no(r.bank_account)
                ctx['client_name'] = r.client_name
            ctx['mobile'] = user.userprofile.mobile_phone
            ctx['cert_type'] = user.userprofile.cert_type
            tpl = 'customer/finance/ab/rescind/step2.html'
            return render(request, tpl, ctx)
        else:
            return redirect('customer:finance-ab-sign_in_out_home')

    @need_market_opening
    def post(self, request, *args, **kwargs):
        user = request.user

        ctx = {}
        ctx['frame_id'] = self.__class__.__frame_id
        bank = UserBank.objects.filter(user=user,is_rescinded=False, bank_name=u'中国农业银行').last()
        if not bank:
            tpl = 'customer/finance/ab/rescind/suc.html'
            return render(request, tpl, ctx)
        else:
            code = request.data.get('vcode')
            sms = None
            if code:
                sms = SmsVerificationCode.objects.filter(user=user, code=code, status=0,
                                                      type=MobileVerificationCodeForRescindAbBankView.get_vcode_type(),
                                                      expired_time__gte=datetime.now()).last()
            if not code or not sms:
                ctx['bank_account'] = request.data.get('bank_account', '')
                ctx['client_name'] = request.data.get('client_name', '')
                ctx['mobile'] = user.userprofile.mobile_phone
                ctx['vcode'] = code
                tpl = 'customer/finance/ab/rescind/step2.html'
                ctx['vcode_err_msg'] =  u'验证码无效'
                return render(request, tpl, ctx)
            elif sms:
                sms.status = 1
                sms.save()

            ret = self.to_rescind(request, user, bank)
            if ret['code'] == ResultCode.SUCCESS:
                tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_suc.html'
            elif ret['code'] == ResultCode.ERROR_PARAM:
                tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_1.html'
            else:
                tpl = 'customer/finance/ab/sign_in/ab_sign_in_contract_failed.html'
            return render(request, tpl, ret.get('data', {}))

    @classmethod
    def do_rescind_event(cls, request, user, bank):
        ret = cls.to_rescind(request, user, bank)
        return ret

    @classmethod
    def to_rescind(cls, request, user, bank):
        # user = request.user
        data = {}
        data['frame_id'] = cls.__frame_id
        data['user_name'] = user.username
        sign_in_data = {}
        sign_in_data['inst_fund_acc'] = AbSignInOutContractHomeView.get_inst_fund_acc_id(user)

        sign_in_data['client_no'] = bank.client_no
        sign_in_data['bank_account'] = bank.bank_account

        r = AbSignInContractLog.objects.filter(user=user, status=1).order_by('modified_time').last()
        if r:
            sign_in_data['client_name'] = r.client_name
            sign_in_data['cert_id'] = r.cert_id
            sign_in_data['cert_type'] = r.cert_type
        else:
            sign_in_data['client_name'] = user.userprofile.real_name
            sign_in_data['cert_id'] = user.userprofile.identification_card_number
            sign_in_data['cert_type'] = '110001' if r.cert_type!=1 else '610001'

        sign_in_data['inst_serial'] = MarketSignContractService.create_ab_inst_serial()
        d = cls.log_to_db(user, sign_in_data)

        ret = {'code': 0, 'msg': '', 'data': data, }

        try:
            r = RescindContractService().do_event(data=sign_in_data)
            resp = r['data']
            d.code = resp['code']
            d.info = resp['info']
            if r['status']['code'] == 0:  # 成功
                d.client_no = resp['client_no']
                d.serial_no = resp['serial_no']
                d.summary = resp['summary']
                d.status = 1
                bank.is_rescinded = True
                bank.save()
                tpl = 'customer/finance/ab/rescind/suc.html'
            else:
                d.status = 2
                d.sys_comment = r['data']
                data['msgs'] = [r['status']['msg']]
                # tpl = 'customer/finance/ab/rescind/failed.html'

                ret['code'] = ResultCode.FIN_RETURN_ERROR
                ret['msg'] = resp.get('info', '')
            # return HttpResponseRedirect('')
            d.save()
            # return render(request, tpl, data)
            return ret

        except Exception as e:
            logging.exception(e)
            d.status = 2
            d.sys_comment = e
            d.save()
            data = {'msgs': [u'网络异常']}
            # tpl = 'customer/finance/ab/rescind/failed.html'
            # return render(request, tpl, data)
            ret['code'] = ResultCode.NET_ERROR
            return ret

    @classmethod
    def log_to_db(cls, user, data):
        d = AbRescindContractLog()
        d.user = user
        d.status = 3

        d.trade_date = datetime.now().date()
        d.trade_time = datetime.now().time()
        d.inst_serial = data['inst_serial']

        d.bank_account = data['bank_account']
        d.inst_func_acc = data['inst_fund_acc']
        d.client_name = data['client_name']
        d.cert_id = data['cert_id']

        d.user_comment = data.get('comment', '')
        d.save()

        return d


class MobileVerificationCodeForRescindAbBankView(APIView):
    __CODE_TYPE = 7   # 解绑银行卡

    @staticmethod
    def get_vcode_type():
        return MobileVerificationCodeForRescindAbBankView.__CODE_TYPE

    def get(self, request, *args, **kwargs):
        """
        验证码类型为修改手机号
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user

        try:
            code = generate_sms_verification_code()
            mobile = user.userprofile.mobile_phone
            SmsVerificationCode(user=user, code=code, type=self.__class__.__CODE_TYPE,data=mobile,
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


class RechargeView(View):
    tpl = 'customer/assets/recharge/recharge_home.html'

    @need_market_opening
    def get(self, request, *args, **kwargs):
        user = self.request.user

        ctx = {'username':  user.username}

        try:
            ctx['is_business_account'] = UserBank.objects.get(user=user, is_rescinded=False).is_business_account
            self.get_recharge(user)
            ctx['balance'] = UserBalance.objects.get(user=user).balance
        except UserBalance.DoesNotExist:
            ctx['balance'] = 0
        except UserBank.DoesNotExist:
            return redirect('customer:finance-ab-sign_in_out_home')
        ctx['frame_id'] = 'assets'

        return render(request,self.tpl, ctx)

    @need_market_opening
    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.POST

        ctx = {ele[0]: ele[1] for ele in data.items()}
        ctx['username'] = user.username
        ctx['frame_id'] = 'assets'

        flag = self.check_input_data(ctx)
        if flag != 0:  # error
            tpl = 'customer/assets/recharge/recharge_home.html'
            ctx['bank_account_pwd'] = ''
            ctx['balance'] = UserBalance.objects.get(user=user).balance
            return render(request, tpl, ctx)

        try:
            self.recharge_core(user, ctx)
            tpl = 'customer/assets/recharge/recharge_suc.html'

            ctx['recharge'] = data['transfer_amount']

        except UserBank.DoesNotExist as e:
            tpl = 'customer/assets/recharge/recharge_failed.html'
            logging.exception(e)
            ctx['msgs'] = [u'尚未签约或已经解约']
        except FinanceTradeException as e:
            tpl = 'customer/assets/recharge/recharge_failed.html'
            logging.exception(e)
            ctx['msgs'] = e.msgs
        except FinanceSysException as e:
            tpl = 'customer/assets/recharge/recharge_failed.html'
            logging.exception(e)
            ctx['msgs'] = e.msgs
        except Exception as e:
            tpl = 'customer/assets/recharge/recharge_failed.html'
            logging.exception(e)
            ctx['msgs'] = [u'系统出错，充值失败']

        ctx['balance'] = UserBalance.objects.get(user=user).balance
        return render(request,tpl, ctx)

    @classmethod
    def log_to_db(cls, user, data):
        d = AbRechargeWithdrawLog()
        d.user = user
        d.status = 3
        d.event = 1 #出金

        d.trade_date = datetime.now().date()
        d.trade_time = datetime.now().time()
        d.inst_serial = data['inst_serial']

        d.bank_account = data['bank_account']
        d.inst_func_acc = data['inst_fund_acc']
        d.client_name = data['client_name']
        d.client_no = data['client_no']
        d.transfer_amount = data['transfer_amount']

        d.user_comment = data.get('comment', '')
        d.save()

        return d

    __cannot_be_empty = u'不能为空'
    __must_be_digit = u'必须是数字'
    __invalid_length = u'长度不正确'
    __invalid_format = u'格式不正确'

    @classmethod
    def check_input_data(cls, data):
        flag = 0
        for item in data.items():
            if item[0].endswith('_msg'):
                item[1] = ''

        if is_none_or_empty(data.get('transfer_amount')):
            data['transfer_amount_msg'] = cls.__cannot_be_empty
            flag = 1
        elif re.compile('^[0-9]+([.]{0,1}[0-9]{1,2}){0,1}$').match(data['transfer_amount']) is None:
                data['transfer_amount_msg'] = cls.__invalid_format
                flag = 1

        if is_none_or_empty(data.get('bank_account_pwd')):
            data['bank_account_pwd_msg'] = cls.__cannot_be_empty
            flag = 1
        else:
            if not data['bank_account_pwd'].isdigit():
                data['bank_account_pwd_msg'] = cls.__must_be_digit
                flag = 1
            elif len(data['bank_account_pwd']) != 6:
                data['bank_account_pwd_msg'] = cls.__invalid_length
                flag = 1

        return flag

    @classmethod
    def recharge_core(cls, user, data):
        """
        :param user:
        :param data: price:金额。 bank_account_pwd: 银行密码.trade_pwd: 出入金密码，对公账户预设密码
        :return:
        """
        user_bank = UserBank.objects.get(user=user, is_rescinded=False)

        sign_in_data = {}
        sign_in_data['inst_fund_acc'] = AbSignInOutContractHomeView.get_inst_fund_acc_id(user)
        sign_in_data['inst_serial'] = RechargeService.create_ab_inst_serial()
        sign_in_data['client_no'] = user_bank.client_no
        sign_in_data['client_name'] = user_bank.client_name
        sign_in_data['bank_account'] = user_bank.bank_account
        sign_in_data['transfer_amount'] = data['transfer_amount']
        if not user_bank.is_business_account:
            sign_in_data['bank_password'] = data['bank_account_pwd'].encode('utf8')
        else:
            sign_in_data['trade_password'] = data['bank_account_pwd'].encode('utf8')

        d = cls.log_to_db(user, sign_in_data)
        flag = 0

        try:

            bank_name = user_bank.bank_name

            r = RechargeService().do_event(data=sign_in_data)
            resp = r['data']
            d.code = resp['code']
            d.info = resp['info']
            d.serial_no = resp['serial_no']
            d.sys_comment = resp
            if r['status']['code'] == 0:  # 成功
                d.host_serial = resp.get('host_serial', '')
                d.enable_bala = resp.get('enable_bala', '')
                d.status = 1
                with transaction.atomic():
                    UserMoneyChange(user=user, trade_type=1, status=2, price=float(sign_in_data['transfer_amount']),
                            money_bank=bank_name).custom_save()

                    d.save()
            else:
                d.status = 2
                d.sys_comment = r['data']
                data['msgs'] = [r['status']['msg']]
                flag = 1
            d.save()
            if flag != 0:
                raise FinanceTradeException(flag=flag, msgs=data['msgs'])
        except FinanceException as e:
            raise e
        except Exception as e:
            logging.exception(e)
            d.status = 2
            d.sys_comment = e
            d.save()
            data = {'msgs': [u'系统错误']}
            raise FinanceSysException(flag=2, msgs=data['msgs'])

    def get_recharge(self, user):
        return UserBalance.objects.get(user=user).balance


# 提现
class WithDrawView(APIView):
    tpl = 'customer/assets/withdraw/withdraw_home.html'

    @need_market_opening
    def get(self, request, *args, **kwargs):
        user = self.request.user
        ctx = {'username':  user.username}

        try:
            ctx['is_business_account'] = UserBank.objects.get(user=user, is_rescinded=False).is_business_account
            ctx['balance'] = UserBalance.objects.get(user=user).balance
        except UserBalance.DoesNotExist:
            ctx['balance'] = 0
        except UserBank.DoesNotExist:
            return redirect('customer:finance-ab-sign_in_out_home')
        ctx['frame_id'] = 'assets'

        return render(request,self.tpl, ctx)

    @need_market_opening
    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.POST

        ctx = {ele[0]: ele[1] for ele in data.items()}
        ctx['username'] = user.username
        ctx['frame_id'] = 'assets'

        flag = self.check_input_data(user, ctx)
        if flag != 0:  # error
            tpl = 'customer/assets/withdraw/withdraw_home.html'
            ctx['payment_pwd'] = ''
            ctx['balance'] = UserBalance.objects.get(user=user).balance
            return render(request, tpl, ctx)

        try:
            user_balance = UserBalance.objects.get(user=user)
            with transaction.atomic():
                user_balance = UserBalance.objects.select_for_update().get(pk=user_balance.pk)
                if user_balance.balance < float(ctx['transfer_amount']):
                    tpl = 'customer/assets/withdraw/withdraw_failed.html'
                    ctx['msgs'] = [u'余额不足']
                    return render(request, tpl, ctx)
                self.withdraw(user, ctx)
            tpl = 'customer/assets/withdraw/withdraw_suc.html'

            ctx['transfer_amount'] = data['transfer_amount']

        except UserBank.DoesNotExist as e:
            tpl = 'customer/assets/withdraw/withdraw_failed.html'
            logging.exception(e)
            ctx['msgs'] = [u'尚未签约或已经解约']
        except FinanceTradeException as e:
            tpl = 'customer/assets/withdraw/withdraw_failed.html'
            logging.exception(e)
            ctx['msgs'] = e.msgs
        except FinanceSysException as e:
            tpl = 'customer/assets/withdraw/withdraw_failed.html'
            logging.exception(e)
            ctx['msgs'] = e.msgs
        except Exception as e:
            tpl = 'customer/assets/withdraw/withdraw_failed.html'
            logging.exception(e)
            ctx['msgs'] = [u'系统出错，提现失败']

        ctx['balance'] = UserBalance.objects.get(user=user).balance
        return render(request,tpl, ctx)

    @classmethod
    def log_to_db(cls, user, data):
        d = AbRechargeWithdrawLog()
        d.user = user
        d.status = 3
        d.event = 2 #入金

        d.trade_date = datetime.now().date()
        d.trade_time = datetime.now().time()
        d.inst_serial = data['inst_serial']

        d.bank_account = data['bank_account']
        d.inst_func_acc = data['inst_fund_acc']
        d.client_name = data['client_name']
        d.client_no = data['client_no']
        d.transfer_amount = data['transfer_amount']

        d.user_comment = data.get('comment', '')
        d.save()

        return d

    @classmethod
    def withdraw(cls, user, data):
        """
        :param user:
        :param data: price:金额。 bank_account_pwd: 银行密码.trade_pwd: 出入金密码，对公账户预设密码
        :return:
        """
        user_bank = UserBank.objects.get(user=user, is_rescinded=False)

        sign_in_data = {}
        sign_in_data['inst_fund_acc'] = AbSignInOutContractHomeView.get_inst_fund_acc_id(user)
        sign_in_data['inst_serial'] = RechargeService.create_ab_inst_serial()
        sign_in_data['client_no'] = user_bank.client_no
        sign_in_data['client_name'] = user_bank.client_name
        sign_in_data['bank_account'] = user_bank.bank_account
        sign_in_data['transfer_amount'] = data['transfer_amount']
        if not user_bank.is_business_account:
            sign_in_data['bank_password'] = data['bank_account_pwd'].encode('utf8')
        else:
            sign_in_data['trade_password'] = data['bank_account_pwd'].encode('utf8')

        d = cls.log_to_db(user, sign_in_data)
        flag = 0

        try:
            bank_name = user_bank.bank_name
            money_change = UserMoneyChange(user=user, trade_type=2, status=1,market_trade_serial_no=sign_in_data['inst_serial'],
                                           price=float(sign_in_data['transfer_amount']), money_bank=bank_name)
            with transaction.atomic():
                money_change.custom_save()

            r = WithdrawService().do_event(data=sign_in_data)
            resp = r['data']
            d.code = resp['code']
            d.info = resp['info']
            d.serial_no = resp['serial_no']
            d.sys_comment = resp
            if r['status']['code'] == 0:  # 成功
                d.host_serial = resp.get('host_serial', '')
                d.enable_bala = resp.get('enable_bala', '')
                d.status = 1
                with transaction.atomic():
                    original_status = money_change.status
                    money_change.status=2
                    money_change.custom_save(original_status=original_status)
                    d.save()
            else:
                d.status = 2
                data['msgs'] = [r['status']['msg']]
                flag = 1
                d.save()

            if flag != 0:
                raise FinanceTradeException(flag=flag, msgs=data['msgs'])

        except FinanceException as e:
            raise e
        except Exception as e:
            logging.exception(e)
            d.status = 2
            d.sys_comment = e
            d.save()
            data = {'msgs': [u'系统错误']}
            raise FinanceSysException(flag=2, msgs=data['msgs'])

    __cannot_be_empty = u'不能为空'
    __must_be_digit = u'必须是数字'
    __invalid_length = u'长度不正确'
    __invalid_format = u'格式不正确'

    @classmethod
    def check_input_data(cls, user, data):
        flag = 0
        for item in data.items():
            if item[0].endswith('_msg'):
                item[1] = ''

        if is_none_or_empty(data.get('transfer_amount')):
            data['transfer_amount_msg'] = cls.__cannot_be_empty
            flag = 1
        elif re.compile('^[0-9]+([.]{0,1}[0-9]{1,2}){0,1}$').match(data['transfer_amount']) is None:
                data['transfer_amount_msg'] = cls.__invalid_format
                flag = 1

        if is_none_or_empty(data.get('payment_pwd')):
            data['payment_pwd_msg'] = cls.__cannot_be_empty
            flag = 1
        else:
            if not check_password(data.get('payment_pwd'), user.userprofile.pay_pwd):
                data['payment_pwd_msg'] = u'密码不匹配'
                flag = 1

        if is_none_or_empty(data.get('bank_account_pwd')):
            data['bank_account_pwd_msg'] = cls.__cannot_be_empty
            flag = 1
        else:
            if not data['bank_account_pwd'].isdigit():
                data['bank_account_pwd_msg'] = cls.__must_be_digit
                flag = 1
            elif len(data['bank_account_pwd']) != 6:
                data['bank_account_pwd_msg'] = cls.__invalid_length
                flag = 1

        return flag
