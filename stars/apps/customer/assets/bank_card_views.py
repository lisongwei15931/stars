# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from stars.apps.commission.models import UserBank
from stars.apps.customer.assets.forms import BankCardForm
from stars.apps.customer.assets.utils import *
from stars.apps.customer.safety.models import SmsVerificationCode


class BankCardListView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        cards = []
        for ele in UserBank.objects.filter(user=user, is_rescinded=False):
            d = {'name': ele.bank_name,
                 'num': mask_bank_card_no(ele.bank_account),
                 'tel': ele.tel,
                 'img_url': BankData.BANK_IMG_URLS.get(ele.bank_name),
                 }
            cards.append(d)

        tpl = 'customer/assets/bank_card/bank_card_index.html'
        m = {'cards': cards,
             'frame_id': 'bank_card',
             }
        return render(request, tpl, m)


class AddBankCardView(APIView):
    __bank_img_urls = {
                        # '中国工商银行': 'images/ABC.png',
                        '中国农业银行': 'images/ABC.png',
                        # '中国银行': 'images/',
                        '中国建设银行': 'images/CCB.png',
                        # '交通银行': 'images/',
                        # '中国邮政银行': 'images/',
                        '招商银行': 'images/CMB.png',}

    def get(self, request, *args, **kwargs):
        tpl = 'customer/assets/bank_card/add_bank_card.html'
        bank_choices = BankData.BANK_CHOICES
        m = {
            'bank_choices': bank_choices,
             'frame_id': 'bank_card',
             }
        return render(request, tpl, m)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        # data['user'] = user
        form = BankCardForm(user, data)

        ctx = {'frame_id': 'bank_card',
               'bank_choices': BankData.BANK_CHOICES,
               }
        is_valid = form.is_valid()
        if is_valid :#and \
                # SmsVerificationCode.objects.filter(user=user,
                #                                    data=data.get('tel'),
                #                                    type=6,
                #                                    status=0,
                #                                    expired_time__gte=datetime.now(),
                #                                    code=data.get('vcode'),).exists:
            UserBank(user=user,
                     bank_account=data['bank_account'],
                     bank_name=data['bank_name'],
                     tel=data['tel']).save()
            # form.save()
            tpl = 'customer/assets/bank_card/add_bank_card_suc.html'
            return render(request, tpl, ctx)
        else:
            if not is_valid:
                if not data.get('vcode'):
                    ctx['vcode_err_msg'] = u'这个字段是必填项。'
                else:
                    ctx['vcode_err_msg'] = u'手机或验证码无效'
            tpl = 'customer/assets/bank_card/add_bank_card.html'
            ctx['vcode'] = data.get('vcode', '')
            ctx['form'] = form
            return render(request, tpl, ctx)

