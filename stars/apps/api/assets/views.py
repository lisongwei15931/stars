# coding=utf-8
import logging

from rest_framework.response import Response

from stars.apps.api.common.views import CommonPermissionAPIView
from stars.apps.api.error_result import err_result, SUCCESS_CODE, SYSTEM_ERR_CODE, ERROR_PARAM
from stars.apps.customer.assets.views import AssetsView


class AssetsSummaryView(CommonPermissionAPIView):

    def get(self, request, format=None):
        """
        获取用户自己的资产信息
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        try:
            user = request.user
            r = AssetsView.get_income_summary(user)

            m = err_result(SUCCESS_CODE, u'获取资产信息成功').msg
            m['data'] = r
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取资产信息失败').msg)

class AssetsIncomeListView(CommonPermissionAPIView):


    def get(self, request, flag, format=None):
        """
        获取用户自己的资产信息
        :param request:
        :param flag: detail:资产明细；locked:冻结明显
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        data = request.GET
        try:
            page_offset = int(data.get('page', 1))
            if page_offset < 1:
                page_offset = 1
            if 'num'in data:
                row_per_page = int(data.get('num'))
            else:
                row_per_page = None

            flag = {'details': 1, 'locked': 2}[flag]
        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)

        try:

            user = request.user
            r = AssetsView.get_income_list(user, flag=flag,
                                           start_time=None, end_time=None,
                                           page_offset=page_offset, row_per_page=row_per_page)

            m = err_result(SUCCESS_CODE, u'获取资产信息成功').msg
            m['page_count'] = r['page_count']
            m['page_index'] = r['page_index']
            m['next_page_index'] = min(m['page_index']+1, m['page_count'])
            m['data'] = []
            for ele in r['income_list_{}'.format(flag)]:
                t = {}
                t['modified_date'] = ele.modified_date
                t['modified_time'] = ele.modified_time
                t['title'] = ''
                t['type'] = ''

                t['opposite_side'] = ''
                t['status'] = ''
                if flag == 1:
                    if ele.trade_type == 5 or ele.trade_type == 8 or ele.trade_type == 9:
                        if ele.product:
                             t['title'] = ele.product.title
                    elif ele.trade_type == 13:
                         t['title'] = ele.pickup_detail_id
                    elif ele.trade_type == 1:
                        t['title'] = u'充值'
                    elif ele.trade_type == 2:
                        t['title'] = u'提现'
                    elif ele.trade_type == 15:
                        t['title'] = u'出售'
                        
                    if ele.trade_type == 5:
                        t['type'] = u'购买'
                    elif ele.trade_type == 8:
                        t['type'] = u'进货'
                    elif ele.trade_type == 9:
                        t['type'] = u'出售'
                    elif ele.trade_type == 12:
                        t['type'] = u'提货'
                    elif ele.trade_type == 15:
                        t['type'] = u'手续费'

                    if ele.status == 2 :
                        if ele.trade_type == 5 or ele.trade_type == 8 or ele.trade_type == 9 :
                            t['status'] = u'交易'
                        elif ele.trade_type == 12:
                            t['status'] = u'提货'
                        else:
                            t['status'] = u'成功'
                    elif ele.status == 1 :
                        t['status'] = u'进行中'
                    elif ele.status == 3 :
                        t['status'] = u'失败'

                    if ele.money_bank_id:
                        t['opposite_side'] = '{ele.money_bank_id.bank_name} 尾号{}'.format(ele.money_bank_id.bank_name, ele.money_bank_id.bank_account[:-4])

                    if ele.trade_type == 2 or ele.trade_type == 3 or ele.trade_type == 5 or ele.trade_type == 6 or ele.trade_type == 8 or ele.trade_type == 10 or ele.trade_type == 12 or ele.trade_type == 15:
                        t['money'] = -ele.price
                    else:
                        t['money'] = -ele.price

                else:
                    if ele.trade_type == 1 or ele.trade_type == 2:
                        if ele.product_title:
                             t['title'] = ele.product_title
                    else:
                         t['title'] = ele.pickup_detail_id
                        
                    if ele.trade_type == 1:
                        t['type'] = u'购买'
                    elif ele.trade_type == 2:
                        t['type'] = u'进货'
                    elif ele.trade_type == 10:
                        t['type'] = u'提货'

                    if ele.trade_type == 1 or ele.trade_type == 2:
                        if ele.status == 1:
                            t['status'] = u'待成交'
                        elif ele.status == 2:
                            t['status'] = u'部分成交'
                    else :
                        t['status'] = u'冻结'

                    if ele.total > 0:
                        t['money'] = -ele.total
                    else:
                        t['money'] = -ele.total
      
                m['data'].append(t)
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取资产信息失败').msg)



