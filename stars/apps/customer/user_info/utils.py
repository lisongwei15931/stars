# -*- coding: utf-8 -*-
from __future__ import division
from stars.apps.customer.safety.common_const import Const

_BASE_ID_INDEX = 10000000


def get_user_inst_fund_acc_id(user):
    """
    获取用户资金帐号
    :param user: user model
    :return:  用户资金帐号（数字）
    """
    return _BASE_ID_INDEX + user.id


def get_user_id_from_inst_account_id(inst_account_id):
    """
    根据用户资金帐号获取用户id
    :param inst_account_id: 数字
    :return: 用户id
    """
    if type(inst_account_id) == 'int':
        return inst_account_id - _BASE_ID_INDEX
    else:
        return int(inst_account_id) - _BASE_ID_INDEX


def mask_bank_card_no(no):
    if no:
        s = '*'*(len(no)-4) + no[-4:]
        r = s[:4] + ' '
        for i in range(1, (len(no)+3)//4):
            r += s[4*i:4*(i+1)] + ' '
        return r
    return no


def is_valid_bank_card_num(num):
    r = num.replace(' ','')
    return 20 > len(r) > 10 and r.isdigit()


def is_valid_mobile(num):
    prefix=['130','131','132','133','134','135','136','137','138','139',
                 '150','151','152','153','156','158','159','170', '172',
                 '178','181', '182','183','185','186','187','188','189']

    return num and len(num) == 11 and num.isdigit() and num[0:3] in prefix


class _BankData(Const):
    BANK_IMG_URLS = {
                        # '中国工商银行': 'images/ABC.png',
                        u'中国农业银行': u'images/ABC.png',
                        # '中国银行': 'images/',
                        u'中国建设银行': u'images/CCB.png',
                        # '交通银行': 'images/',
                        # '中国邮政银行': 'images/',
                        u'招商银行': u'images/CMB.png',}
    BANK_CHOICES = set(BANK_IMG_URLS.keys())

BankData = _BankData()


def is_valid_bank(name):
    return name in BankData.BANK_CHOICES



