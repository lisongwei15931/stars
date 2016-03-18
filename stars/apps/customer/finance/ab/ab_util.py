# -*- coding: utf-8 -*-
from __future__ import division

import logging
import os
import random
import string
from datetime import datetime

from stars.apps.customer.finance.models import AgriculturalBankOriginalKey, AgriculturalBankEncKey
from utils import is_none_or_empty
import stars.settings


def make_header(msg_len, msg_type, trade_no, mch_id, mac):
    return 'X1.0{msg_len:0>5}{head_msg_type}{trade_no}{mch_id}10{mac}00000000'.format(msg_len=msg_len,
                                                                                 msg_type=msg_type,
                                                                                 trade_no=trade_no,
                                                                                 mch_id=mch_id,
                                                                                 mac=mac)
def get_service_name_for_ab(inst_code):
    return {
        # 银行发起的交易
        '20003': 'a1',	  # 联通性检测
        '21001': 'a2',	  # 签约
        '21004': 'a3',	  # 解约
        '22001': 'a4',	  # 入金申请
        '22002': 'a5',	  # 出金申请
        '22005': 'a6',	  # 入金审核查询
        '22006': 'a7',	  # 出金审核查询
        '23004': 'a8',	  # 查询市场资金余额
        '31101': 'a9',	  # 文件生成通知
        # 市场发起的交易
        '10001': 'b1',	  # 市场签到
        '10002': 'b2',	  # 市场签退
        '10008': 'b3',	  # 上传/下载文件
        '10009': 'b4',	  # 密钥交换
        '10010': 'b5',	  # 密钥交换确认
        '13011': 'b6',	  # 闭市
        '11001': 'b7',	  # 签约
        '11004': 'b8',	  # 解约
        '12001': 'b9',	  # 入金
        '12002': 'ba',	  # 出金
        '12003': 'bb', # 冲入金
        '12004': 'bc', # 冲出金
        # '12005': 'bd', # 入金审核通知  暂不开发
        '12006': 'be', # 出金审核通知
        '13003': 'bf', # 出入金流水查询
        '13004': 'bg', # 单笔出入金流水状态查询
        '11009': 'bh', # 查询账户余额
        '13019': 'bi', # 市场清算确认通知
        '14001': 'bj', # 个人客户身份验证
    }.get(inst_code)


def create_ab_inst_serial(service):
    s = '{:0<2}'.format(service) + '{:0<14}'.format(datetime.now().strftime('%Y%m%d%H%M%S%f')[2:16])+''.join(random.sample(string.letters, 4))

    assert(len(s) == 20)
    return s


ori_mac_key = 'LwxICXGAiQR6BTxt'
_init_mac_key = '12345678'
_init_pack_key = '12345678'
# init_pack_key = ''.join([chr(i) for i in [1,2,3,4,5,6,7,8]])
_init_pin_key = '12345678'
ori_pack_key = 'gBujQ2Z8HtlOiDe8'
ori_pin_key = 'knvWJnuOF9LVwLIl'
_pack_key = None
_pin_key = None
_mac_key = None


def get_ori_key():
    r = AgriculturalBankOriginalKey.objects.first()
    if not r:
        return r.package, r.pin, r.mac
    else:
        return ori_pack_key, ori_pin_key, ori_mac_key


def get_key():
    # TODO
    global _pack_key
    global _pin_key
    global _mac_key

    # if not _pack_key and os.path.exists('./pack_key.txt'):
    #     with open('./pack_key.txt', 'rb') as f:
    #         _pack_key = f.read()
    # if not _pin_key and os.path.exists('./pin_key.txt'):
    #     with open('./pin_key.txt', 'rb') as f:
    #         _pin_key = f.read()
    # if not _mac_key and os.path.exists('./mac_key.txt'):
    #     with open('./mac_key.txt', 'rb') as f:
    #         _mac_key = f.read()
    try:
        r = AgriculturalBankEncKey.objects.latest('modified_time')
        if not _pack_key:
            _pack_key = r.package if isinstance(r.package, str) else r.package.encode('utf8')
        if not _pin_key:
            _pin_key = r.pin if isinstance(r.pin, str) else r.pin.encode('utf8')
        if not _mac_key:
            _mac_key = r.mac if isinstance(r.mac, str) else r.mac.encode('utf8')
    except Exception as e:
        logging.exception(e)

    mac_key = _mac_key if _mac_key else _init_mac_key
    pack_key = _pack_key if _pack_key else _init_pack_key
    pin_key = _pin_key if _pin_key else  _init_pin_key
    return pack_key, pin_key, mac_key


def set_key(pack_key=None, pin_key=None, mac_key=None, expired_date=None):
    # FIXME 保存到数据库
    global _pack_key
    global _pin_key
    global _mac_key

    if pack_key:
        _pack_key = pack_key
    if pin_key:
        _pin_key = pin_key
    if mac_key:
        _mac_key = mac_key

    AgriculturalBankEncKey(package=_pack_key, pin=_pin_key, mac=_mac_key, expire_time=expired_date).save()
    # with open('./pack_key.txt', 'wb') as f:
    #     f.write(pack_key)
    # with open('./pin_key.txt', 'wb') as f:
    #     f.write(pin_key)
    # with open('./mac_key.txt', 'wb') as f:
    #     f.write(mac_key)


from ctypes import *
AES_NROUNDS_BYTESTOKEY = c_int(5)
ENCRYPT = 0
DECRYPT = 1
AES_ENCMODE_128CBC = 0
AES_ENCMODE_192CBC = 1
AES_ENCMODE_256CBC =2

import platform
if platform.system() in ['Windows']:
    if platform.node() == 'sky':
        from ctypes import windll as dll
        try:
            so = dll.LoadLibrary('./DLL.dll')
        except Exception as e:
            logging.exception(e)
            so = None
    else:
        so = None
elif platform.system() in ['Linux']:
    from ctypes import cdll as dll
    so_path = os.path.join(stars.settings.BASE_DIR, 'ab_crypt.so')
    so = dll.LoadLibrary(so_path)

else:
    so = None


def ab_encrypt_msg(msg, key):
    if is_none_or_empty(msg):
        return msg
    n = len(msg) % 16
    if n != 0:
        n = len(msg)+16-n
    else:
        n = len(msg)
    o = create_string_buffer(n+40)
    m = so.AES_Data(ENCRYPT, key, msg, o, len(msg), AES_ENCMODE_128CBC)

    i = m if m > len(msg) else len(msg)
    with open('r_c_msg.txt', 'wb') as w:
        w.write(o.raw[:i])

    # o_hex = hexlify(o.value)

    # o2 = create_string_buffer(i+100)
    # # n=len(o.value)
    # a = o.raw[:i]
    # so.AES_Data(DECRYPT, key, a, o2, len(a), AES_ENCMODE_128CBC)
    # assert(o2.value==msg)

    return o.raw[:i]


def ab_decrypt_msg(msg, key):
    if is_none_or_empty(msg):
        return msg

    n = len(msg) % 16
    if n != 0:
        n = len(msg)+16-n
    else:
        n = len(msg)
    o = create_string_buffer(n+40)
    m = so.AES_Data(DECRYPT, key, msg, o, n, AES_ENCMODE_128CBC)
    return o.raw[:m] if m > len(msg) else o.raw[:len(msg)]


def ab_encrypt_password(msg, key):
    if is_none_or_empty(msg):
        return msg
    n = len(msg) % 16
    if n != 0:
        n = len(msg)+16-n
    else:
        n = len(msg)
    # n = len(msg)
    n *= 2
    o = create_string_buffer(n)
    m=so.AES_PasswordByKey(ENCRYPT, msg[:], o,  key)

    s = o.raw[:n]
    return s
    # o_hex = hexlify(o.value)
    # o2 = create_string_buffer(1000)
    # n=len(o.value)
    # so.AES_Data(DECRYPT, "12345678", o.value, o2, n, AES_ENCMODE_128CBC)
    # assert(o2.value==msg)


def ab_decrypt_password(msg, key):
    if is_none_or_empty(msg):
        return msg
    n = len(msg) % 16
    if n != 0:
        n = len(msg)+16-n
    else:
        n = len(msg)

    # n += 10

    o = create_string_buffer(n)
    m = so.AES_PasswordByKey(DECRYPT, msg, o, key)
    return o.raw[:n/2]

# def _encrypt_msg(msg, key):
#     if isinstance(msg, str):
#         msg = msg.decode('utf-8').encode('gbk')
#     elif isinstance(msg,unicode):
#         msg =  msg.encode('gbk')
#
#     o = AES.new(key, AES.MODE_ECB)
#     n = 16 - len(msg)%16
#     if n != 16:
#         msg += chr(0)*n
#         c_text = o.encrypt(msg)
#
#     c_text = o.encrypt(msg)
#
#     assert(msg == o.decrypt(c_text))
#
#     return c_text


def is_successful_result_code(result_code):
    """
    判断返回码是否为成功
    :param result_code: 返回码
    :return: True,成功；False，失败
    """
    return result_code[2:] == '0000'


def get_mac_and_msg_size_from_header(header):
    """
    从包头中返回包数据的mac、长度
    :param header: 包头
    :return:
    """
    mac = header[-16: -8]
    msg_size = header[4: 9]

    return mac, msg_size


def check_header(header):
    pass # TODO


def check_msg(msg, mac, msg_size):
    pass # TODO

def make_mac(bytes_data, key):
    # 不进行mac检测
    # if not make_mac:
    #     raise ValueError
    # r = chr(0)*8
    #
    # for i in range(len(bytes_data)//8):
    #     r = strxor(r, bytes_data[i*8:i*8+8])
    #
    # dale = bytes_data[len(bytes_data)//8*8:]
    # if dale:
    #     dale += chr(0) * (8-len(dale))
    #     r = strxor(r, dale)
    # des = DES.new(key, DES.MODE_ECB)
    # des_s = des.encrypt(r)

    des_s = chr(0)*8

    return des_s


def check_mac(bytes_data, mac, key):
    return mac == make_mac(bytes_data, key)


    # import OpenSSL
    # import tlslite.utils.openssl_aes
    #
    # OpenSSL.crypto.
    # EVP_BytesToKey(cipher, EVP_sha1(), NULL, key_data, key_data_len, AES_NROUNDS_BYTESTOKEY, key, iv)

