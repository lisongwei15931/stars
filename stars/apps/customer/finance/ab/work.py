# -*- coding: utf-8 -*-
import logging
import os
from collections import namedtuple
from datetime import *

from dateutil import parser
from decimal import Decimal
from django.dispatch import receiver
import django.utils.timezone

from stars import settings
from stars.apps.customer.finance.ab.service.ab_client_service import MarketSignInClientService, \
    MarketSignOutClientService, MarketCloseClientService, MarketDownloadFileClientService, TransferKeyClientService, \
    ConfirmTransferKeyClientService
from stars.apps.customer.finance.ab.service.ab_service import AbService
from stars.apps.customer.finance.ab.signal import received_file_names_done, download_files_done
from stars.apps.customer.finance.models import AbRechargeWithdrawLog, AbBankStatement, AbRechargeWithdrawErrorStatus, \
    AgriculturalBankEncKey
from stars.apps.customer.user_info.utils import get_user_id_from_inst_account_id


def ab_start_trade():
    try:
        r = MarketSignInClientService().do_event(data=None)
        if r['status']['code'] == 0:  # 成功
            pass
        else:
            handle_market_sign_in_failed(r)

        _check_and_create_new_key()
    except Exception as e:
        logging.exception(e)


def _check_and_create_new_key():
    r = AgriculturalBankEncKey.objects.last()
    if not r or (django.utils.timezone.now() + timedelta(days=1)) < r.expire_time:
        resp = TransferKeyClientService().do_event(data=None)
        logging.exception(' transferkey response: ')
        logging.exception(resp)
        if resp and resp['status']['code'] == 0:
            d = resp['data']
            r = ConfirmTransferKeyClientService().do_event(data=None, keys=(d['pack_key'], d['pin_key'], d['mac_key']))
            logging.exception(' confirm transferkey response: ')
            logging.exception(r)


def ab_end_trade():
    # 银商通测试环境不执行，否则第二天不能开市，需要电话联系银商通技术人员手动清算后，才能开市 by lwj 20151208
    pass
    # return _ab_end_trade()


def _ab_end_trade():
    try:
        r = MarketSignOutClientService().do_event(data=None)
        if r['status']['code'] == 0:  # 成功
            r = MarketCloseClientService().do_event(data=None)
            if r['status']['code'] == 0:  # 成功
                pass
            else:
                handle_market_close_failed(r)
        else:
            handle_market_sign_out_failed(r)

        _check_and_create_new_key()
    except Exception as e:
        logging.exception(e)


def _create_error_statement_record(bank_trans_data, market_statement, status):
    b = None
    if bank_trans_data:
        b = AbBankStatement(trans_date=bank_trans_data.trans_date,
                            trans_code=bank_trans_data.trans_code,
                            source_side=bank_trans_data.source_side,
                            serial_no=bank_trans_data.serial_no,
                            amount=bank_trans_data.amount,
                            client_no=bank_trans_data.clent_no,
                            busi_type=bank_trans_data.busi_type,
                            money_kind=bank_trans_data.money_kind,
                            inst_func_acc=bank_trans_data.inst_func_acc,
                            charge=bank_trans_data.charge,
                            )
        b.user_id = get_user_id_from_inst_account_id(b.inst_func_acc)

        b.inst_serial = bank_trans_data.inst_serial
        b.bank_account = bank_trans_data.bank_account
        b.reserve1 = bank_trans_data.reserve1
        b.reserve2 = bank_trans_data.reserve2

        if bank_trans_data.trans_time:
            b.trans_time = bank_trans_data.trans_time

        b.save()
    a = AbRechargeWithdrawErrorStatus(bank_statement=b, market_statement=market_statement, status=status).save()
    return a


def _do_settlement(**kwargs):
    TransData = namedtuple('TransData', 'trans_date bank_account trans_time source_side trans_code serial_no client_no '
                                        'inst_no busi_type money_type fund_acc inst_serial amount charge '
                                        'reserve1 reserve2')
    ds = {}
    inst_serials = set()

    for file_path in kwargs['files']:
        with open(file_path, mode='r') as f:
            for line in f.readlines():
                d = line.strip('|')

                d = TransData._make(d)
                if d.inst_no == AbService.trade_no:
                    try:
                        Decimal(d.amount)
                    except Exception as e:
                        pass
                    else:
                        ds[d.inst_serial] = d
                        inst_serials.add(d.inst_serial)

    error_trans = []
    # 错误：状态（①银行成功市场失败②市场成功银行失败③银行成功市场不存在④市场成功银行不存在）或金额不一致

    #状态（①银行成功市场失败）或金额不一致
    for ele in AbRechargeWithdrawLog.objects.filter(inst_serial__in=inst_serials):
        inst_serials.pop(ele.inst_serial)
        status = None
        if ele.status != 1:
            status=1
        elif ele.transfer_amount != Decimal(ds[ele.inst_serial].amount):
            status=3

        if status is not None:
            r = _create_error_statement_record(ds[ele.inst_serial], ele, status)
            error_trans.append(r)

    for ele in inst_serials: #③银行成功市场不存在
        r = _create_error_statement_record(ds[ele], None, status=1)
        error_trans.append(r)


    the_day = kwargs['the_day']
    # ②市场成功银行失败或不存在
    for ele in AbRechargeWithdrawLog.objects.filter(trade_date=the_day, status=1).exclude(inst_serial__in=inst_serials):
        r = _create_error_statement_record(None, ele, status=2)
        error_trans.append(r)

    return error_trans


@receiver(received_file_names_done, dispatch_uid="4759dc6e-fa08-4785-bf56-c911abb9162a")
def receive_files_from_ab_server(sender, **kwargs):
    the_day = kwargs['the_day']

    files = {}
    base_dir = settings.FINANCE_ROOT

    for file_name in kwargs['file_names']:

        try:
            save_file_path = os.path.join(base_dir, 'ab')
            if isinstance(the_day, str):
                save_file_path = os.path.join(save_file_path, parser.parse(the_day).strftime('%Y%m%d'))
            elif isinstance(the_day, (datetime, date)):
                save_file_path = os.path.join(save_file_path, the_day).strftime('%Y%m%d')
            else:
                raise ValueError
            save_file_path = os.path.join(save_file_path, file_name)

            m = {'file_name': file_name, 'save_file_path': save_file_path}
            r = MarketDownloadFileClientService().do_event(m)
            files['file_name'] = r['saved_file_path']


        except Exception as e:
            logging.exception(e)

    download_files_done.send(sender=None, files=files, the_day=the_day)


@receiver(download_files_done, dispatch_uid="6a21c52d-1fb8-4d3c-9d41-a3aaca689359")
def settle_market(sender, **kwargs):
    files = []
    for file_name, file_path in kwargs['files'].items():
        if file_name.startswith('bTransfer_'):
            files.append(file_path)

    error_trans = _do_settlement(files=files)
    if error_trans:
        # TODO 是否通知？
        pass


def handle_market_sign_in_failed(data):
    pass


def handle_market_sign_out_failed(data):
    pass


def handle_market_close_failed(data):
    pass

