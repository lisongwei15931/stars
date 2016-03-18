# coding=utf-8
import logging

from django.db import transaction
from rest_framework.exceptions import *
from rest_framework.response import Response

from stars.apps.api.common.views import CommonPermissionAPIView
from stars.apps.api.error_result import err_result, SUCCESS_CODE, SYSTEM_ERR_CODE, ERROR_PARAM
from stars.apps.commission.models import UserBank, UserBalance, UserMoneyChange
from stars.apps.customer.finance.ab.views import AbSignInContractView, AbRescindContractView, RechargeView, WithDrawView
from stars.apps.customer.finance.common_const import ResultCode
from stars.apps.customer.finance.finance_exception import FinanceTradeException, FinanceSysException


class AppAbSignInContractView(CommonPermissionAPIView):

    __BE_USED_CODE = ''
    __FIN_RETURN_ERROR = ''

    def post(self, request, format=None):
        """
        银商通签约
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        try:
            ret = AbSignInContractView.do_sign_event(request, request.user)
            if ret['code'] == ResultCode.SUCCESS:
                return Response(err_result(SUCCESS_CODE, u'签约成功').msg)
            elif ret['code'] == ResultCode.ERROR_PARAM:
                return Response(err_result(ERROR_PARAM, u'参数错误').msg)
            elif ret['code'] == ResultCode.BE_USED:
                return Response(err_result(self.__BE_USED_CODE, u'该银行账户已经被其他用户签约').msg)
            elif ret['code'] == ResultCode.FIN_RETURN_ERROR:
                return Response(err_result(self.__FIN_RETURN_ERROR, ret.get('msg', u'签约失败')).msg)
            else:
                return Response(err_result(SYSTEM_ERR_CODE, u'签约失败').msg)

        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'签约失败').msg)


class AppAbRescindContractView(CommonPermissionAPIView):

    __BE_USED_CODE = ''
    __FIN_RETURN_ERROR = ''

    def post(self, request, format=None):
        """
        银商通解约
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        try:
            ret = AbRescindContractView.do_sign_event(request, request.user)
            if ret['code'] == ResultCode.SUCCESS:
                m = err_result(SUCCESS_CODE, u'解约成功').msg
                return Response(m)
            elif ret['code'] == ResultCode.ERROR_PARAM:
                m = err_result(ERROR_PARAM, u'参数错误').msg
                return Response(m)
            elif ret['code'] == ResultCode.FIN_RETURN_ERROR:
                m = err_result(self.__FIN_RETURN_ERROR, ret.get('msg', u'解约失败')).msg
                return Response(m)
            else:
                return Response(err_result(SYSTEM_ERR_CODE, u'解约失败').msg)

        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'解约失败').msg)


class AppAbRechargeView(CommonPermissionAPIView):

    __FIN_RETURN_ERROR = ''

    def post(self, request, format=None):
        """
        充值
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        data = {ele[0]: ele[1] for ele in request.data.items()}
        flag = RechargeView.check_input_data(data)
        if flag != 0:
            m = err_result(ERROR_PARAM, u'参数错误').msg
            return Response(m)
        user = request.user
        try:
            RechargeView.recharge_core(user, data)
            m = err_result(SUCCESS_CODE, u'解约成功').msg
            return Response(m)
        except UserBank.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'尚未签约或已经解约').msg)
        except FinanceTradeException as e:
            logging.exception(e)
            return Response(err_result(self.__FIN_RETURN_ERROR, e.msgs[0] if e.msgs else u'尚未签约或已经解约').msg)
        except FinanceSysException as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'系统错误，充值失败').msg)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'系统错误，充值失败').msg)


class AppAbWithdrawView(CommonPermissionAPIView):

    __FIN_RETURN_ERROR = ''
    __NO_ENOUGH_BALANCE = ''

    def post(self, request, format=None):
        """
        提现
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        user = self.request.user
        data = {ele[0]: ele[1] for ele in request.data.items()}
        flag = WithDrawView.check_input_data(user, data)
        if flag != 0:
            m = err_result(ERROR_PARAM, u'参数错误').msg
            return Response(m)
        user = request.user
        try:
            user_balance = UserBalance.objects.get(user=user)
            with transaction.atomic():
                user_balance = UserBalance.objects.select_for_update().get(pk=user_balance.pk)
                if user_balance.balance < float(data['transfer_amount']):
                    return Response(err_result(SYSTEM_ERR_CODE, u'余额不足').msg)
                WithDrawView.withdraw(user, data)
            m = err_result(SUCCESS_CODE, u'提现成功').msg
            return Response(m)
        except UserBank.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'尚未签约或已经解约').msg)
        except FinanceTradeException as e:
            logging.exception(e)
            return Response(err_result(self.__FIN_RETURN_ERROR, e.msgs[0] if e.msgs else u'提现失败').msg)
        except FinanceSysException as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'系统错误，提现失败').msg)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'系统错误，提现失败').msg)
