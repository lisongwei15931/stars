 # -*- coding: utf-8 -*-
from __future__ import division

import json
from collections import defaultdict
from datetime import datetime, timedelta

from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import  connection
from django.db.models import Sum, Count, Q, F, FloatField
from django.db.models.functions import Coalesce
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from stars.apps.commission.models import UserMoneyChange, UserBalance, UserAssetDailyReport
from stars.apps.commission.views import UserProduct
from stars.apps.customer.assets.utils import AssetsUtil
from stars.apps.customer.safety.utils import convert_none_or_empty_to_0


class AssetsView(APIView):
    tpl = 'customer/assets/account_assets.html'
    __row_per_page = 20

    def get(self, request, *args, **kwargs):
        user = request.user
        data = request.GET

        period_type = data.get('period_type')
        flag = data.get('flag')
        flag = 1 if flag != '2' else 2
        ctx = {'flag': flag, 'period_type': period_type}

        start_time, end_time = self.get_date_range(period_type)

        period_cond = 'period_type={}'.format(period_type) if period_type else ''
        if period_type == 'start-end':
            if start_time:
                period_cond += '&start_date={}'.format(start_time)
            if end_time:
                period_cond += '&end_date={}'.format(end_time)
            if period_cond.startswith('&'):
                period_cond =period_cond[1:]
            ctx['start_date'] = start_time
            ctx['end_date'] = end_time
        ctx['period_cond'] = period_cond
        # ctx = {'flag': flag, 'period_type': period_type, 'start_date': start_time, 'end_date': end_time, 'period_cond': period_cond}

        try:
            page_idx = data.get('page')
            if not page_idx:
                page_idx = 1
            else:
                page_idx = int(page_idx)
        except ValueError:
            return Response(status=http_status.HTTP_400_BAD_REQUEST)

        is_verified = True if hasattr(user, 'userprofile') and user.userprofile.audit_status else False

        ctx['user'] = {'is_verified': is_verified, 'name': user.username, 'fund_acc_id': user.userprofile.uid}

        ctx['assets_summary'] = self.get_income_summary(user)
        if end_time and period_type == 'start-end':
            end_time = (parser.parse(end_time) + timedelta(days=1)).strftime('%Y-%m-%d')
        ctx['income_history'] = self.get_income_list(user=user, flag=flag, start_time=start_time, end_time=end_time, page_offset=page_idx)

        ctx['frame_id'] = 'assets'

        return render(request,self.tpl, ctx)

    def get_date_range(self, period_type):
        start_time, end_time = None, None
        if period_type == 'start-end':
            start_time, end_time = self.request.GET.get('start_date'), self.request.GET.get('end_date')

        elif period_type == '1_month':
            start_time, end_time = datetime.today() - relativedelta(months=1), datetime.today()
        elif period_type == '3_month':
            start_time, end_time = datetime.today() - relativedelta(months=3), datetime.today()
        elif period_type == '1_year':
            start_time, end_time = datetime.today() - relativedelta(years=1), datetime.today()
        return start_time, end_time

    @classmethod
    def get_income_summary(cls, user):
        today = datetime.today().date()
        # yesterday = today - timedelta(days=1)
        today_assets = UserAssetDailyReport.objects.filter(target_date=today, user=user).first()

        data = defaultdict(float)
        if today_assets:
            data['today_income'] = today_assets.income
            data['today_expenditure'] = today_assets.expenditure
            data['today_beginning_balance'] = today_assets.start_balance  # 期初资金
            data['drawable_num'] = today_assets.can_out_amount
            data['usable_num'] = today_assets.can_use_amount

        row = UserBalance.objects.filter(user=user).last()
        if row:
            data['balance'] = row.balance   # 账户余额
            data['locked_sum'] = row.locked

        # 当前库存商品成本总价
        current_product_total_cost_price = UserProduct.objects.filter(user=user, trade_type=2).aggregate(
            total=Coalesce(Sum(F('quantity')*F('overage_unit_price'), output_field=FloatField()), 0.0))['total']

        data['total_income'], data['yesterday_income'] = AssetsUtil.get_profit(user.id)

        # cursor = connection.cursor()
        # sql ='select sum(ppp) ' \
        #      '  from (select up.product_id,' \
        #      '         sum(up.quantity*case when st.strike_price is not null then st.strike_price else st.opening_price end)  as ppp,' \
        #      '         max(st.created_date) ' \
        #      '        from commission_userproduct as up inner join commission_stockticker as st on (up.product_id = st.product_id)' \
        #       '       where up.user_id=%s and up.trade_type=2' \
        #       '       group by up.product_id) as temp'
        #
        # cursor.execute(sql,[user.id])
        # r = cursor.fetchone()
        #
        # if r and r[0] is not None:
        #     data['market_cap'] = r[0]  # 最新市值

        for ele in  UserProduct.objects.filter(user_id=user.id, trade_type=2):
            if ele.quantity and ele.product.strike_price:
                data['market_cap'] += int(ele.quantity) * float(ele.product.strike_price)
        data['market_increment'] = data['market_cap'] - current_product_total_cost_price  # 商品增值 （所有时间内）

        data['total_assets'] = data['usable_num'] + data['market_cap'] + data['locked_sum']

        return data

    @classmethod
    def get_income_list(cls, user, flag=1, start_time=None, end_time=None, page_offset=1, row_per_page=None):
        total_num = 0
        if not row_per_page or row_per_page < 1:
            limit = cls.__row_per_page
        else:
            limit = row_per_page

        if page_offset < 1:
            page_offset = 1

        if flag == 1:
            q = UserMoneyChange.objects.filter(Q(user=user))
            # 不包含撤单
            q = q.filter((Q(trade_type__in=(5,8,9,12,15)) & Q(status=2)) | Q(trade_type__in=(1,2))) #充值、提现、购买成交、进货成交、出售、提货完成

            if start_time:
                q = q.filter(modified_date__gte=start_time)
            if end_time:
                q = q.filter(modified_date__lt=end_time)

            total_num = convert_none_or_empty_to_0(q.aggregate(Count('pk')).values()[0])

            q = q.prefetch_related('money_bank_id')

            q = q.order_by('-modified_date', '-modified_time')

            paginator = Paginator(q, limit)
            try:
                l = paginator.page(page_offset)
                # for ele in l:
                #     if ele.trade_type == 5:
                #         ele.price += UserMoneyChange.objects.filter(user_id=ele.user_id,order_no=ele.order_no, trade_type_in=[], status=2).aggregate(price=Coalesce(Sum('price'), 0.0))['price']
                        # n = UserMoneyChange.objects.filter(user_id=ele.user_id, status=2).aggregate(price=Coalesce(Sum('price'), 0.0))['price']
                        # ele.price += n
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                l = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                l = paginator.page(paginator.num_pages)

        elif flag == 2:
            # 购买、进货、提货冻结
            # 提货冻结 解冻、驳回parent_id对应冻结id
            from_where_1 = 'from commission_commissionbuy as cc left join catalogue_product as cp on cp.id=cc.product_id '\
                    'where cc.user_id=%(user_id)s and {period1} cc.c_type in (1,2) and cc.status in (1,2) and uncomplete_quantity>0 '
            from_where_2 = 'from commission_usermoneychange as a '\
                    'where a.user_id=%(user_id)s and {period2} a.trade_type=10 ' \
                           ' AND NOT EXISTS (SELECT b.id FROM commission_usermoneychange AS b WHERE b.parent_id_id=a.id AND b.user_id=%(user_id)s AND b.trade_type IN (11,12) )'
            sql1 = 'select cc.id,cc.c_type as trade_type,cc.status,cc.uncomplete_quantity*cc.unit_price as total, cp.title as product_title, "" as pickup_detail_id,' \
                  'date(adddate(cc.modified_datetime,INTERVAL 8 HOUR)) as modified_date, time(adddate(cc.modified_datetime,INTERVAL 8 HOUR)) as modified_time ' + from_where_1 + ' union all '\
                    'select a.id, a.trade_type ,a.status, a.pickup_amount as total,  ' \
                     '"" as product_title, a.pickup_detail_id, a.modified_date, a.modified_time ' + from_where_2

            count_sql = 'select count(*)' + from_where_1 + ' union all select count(*) ' + from_where_2

            period1 = period2 = ''
            params = {'user_id': user.id, 'offset': (page_offset-1)*limit, 'limit': limit}
            if start_time:
                period1 = 'modified_datetime >=%(start_time)s and '
                period2 = 'modified_date >= %(start_time)s and '
                params['start_time'] = start_time
            if end_time:
                # prefix = ' and ' if start_time else ''

                period1 += 'modified_datetime <  %(end_time)s and '
                period2 += 'modified_date <%(end_time)s and '
                params['end_time'] = end_time

            count_sql = count_sql.format(period1=period1, period2=period2)
            total_num = 0
            with connection.cursor() as cursor:
                cursor.execute(count_sql, params)

                for ele in cursor.fetchall():
                    total_num += ele[0]

            sql1 = sql1.format(period1=period1, period2=period2)
            sql = 'select * from (' + sql1 + ') as t order by modified_date desc, modified_time desc limit %(limit)s offset %(offset)s'

            l = list(UserMoneyChange.objects.raw(sql, params=params))

        else:
            assert(False)

        page_count = (total_num+limit-1) // limit
        r = {'page_count': page_count,
             'total_num': total_num,
             'page_index': min(page_count, page_offset),
             'row_per_page': limit,
             'income_list_{}'.format(flag): l}

        # 翻页
        page_enum = []
        start = max(1, page_offset-2 if page_offset != page_count else page_offset-4)
        end = min(page_count, max(6, page_offset+2))
        for page in range(start, end+1):
            page_enum.append(page)

        r['page_enum'] = page_enum

        return r


@login_required
def get_user_income(request):
    user = request.user
    result = {}
    
    try :
        #=======================================================================
        # #昨日收益
        # today = datetime.today().date()
        # yesterday = today - timedelta(days=1)
        # yesterday_icome = UserAssetDailyReport.objects.filter(target_date=yesterday, user=user).values('income')
        # if yesterday_icome :
        #     yesterday_icome = str(yesterday_icome[0]['income'])
        # else :
        #     yesterday_icome = "0.0"
        # #累计收益
        # total_icome = UserAssetDailyReport.objects.filter(user=user).aggregate(Sum('income')).values()
        # if total_icome :
        #     total_icome = str(total_icome[0])
        # else :
        #     total_icome = "0.0"
        #=======================================================================
        #昨日收益
        yesterday_icome = AssetsUtil.get_profit(user.id)[1]
        if yesterday_icome:
            yesterday_icome = yesterday_icome
        else :
            yesterday_icome =0.00
        #累计收益
        total_icome = AssetsUtil.get_profit(user.id)[0]
        if total_icome :
            total_icome = total_icome
        else:
            total_icome = 0.00
        #账户余额
        user_balance_last = UserBalance.objects.filter(user=user).last()
        
        if user_balance_last :
            user_balance = user_balance_last.balance
        else :
            user_balance =0.0
    except :
        pass
    
    result = {'yesterday_icome':yesterday_icome,
              'total_icome' :total_icome,
              'user_balance' :user_balance,
              }
    
    return HttpResponse(json.dumps(result),content_type="application/json")