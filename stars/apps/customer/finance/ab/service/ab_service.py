# -*- coding: utf-8 -*-
from __future__ import division

import copy
from collections import namedtuple
from datetime import datetime
from struct import unpack

from stars.apps.customer.finance.ab import ab_util, utils
from stars.apps.customer.finance.ab.common_const import AgriculturalBankTradeConstData


class Handler(object):
    def handle(self):
        pass


class ErrorHandler(Handler):
    def handle(self):
        pass


class SucHandler(Handler):
    def handle(self):
        pass


class AbService(object):
    head_msg_type = 'R'
    trade_no = ''
    msg_template = ''
    trade_source = ''

    __mch_id = AgriculturalBankTradeConstData.INST_NO

    Header = namedtuple('Header', 'api_type ver msg_size head_msg_type trade_no mch_id encryption_flag mac_flag mac reserve')
    __header_fmt = '!1s3s5s1s5s8s1s1s8s8s'

    __key_fields_set = {'BankPassword', 'TradePassword', 'FundPassword', 'InstOprPwd'}

    must_exist_item = set()

    def __init__(self, suc_handler=None, error_handler=None):
        self.suc_handler = suc_handler
        self.error_handler = error_handler

    # def get_msg_template(self):
    #     return msg_template

    @classmethod
    def create_ab_inst_serial(cls):
        return ab_util.create_ab_inst_serial(ab_util.get_service_name_for_ab(cls.trade_no))

    def get_trade_no(self):
        return self.trade_no

    def send_and_receive(self, data):
        raise NotImplemented

    def send(self, data):
        raise NotImplemented

    def receive(self, size):
        raise NotImplemented

    def get_mch_id(self):
        return self.__class__.__mch_id

    def get_key(self):
        return ab_util.get_key()

    def get_date(self):
        return datetime.today().strftime('%Y%m%d')

    def get_time(self):
        return datetime.today().strftime('%H%M%S')

    @staticmethod
    def get_header_from_text(text):
        a=AbService.Header._make(unpack(AbService.__header_fmt, text))
        return a._replace(msg_size=int(a.msg_size))

    def split_header_msg(self, buf):
        if isinstance(buf, list):
            buf = ''.join(buf)

        s = buf[:41]
        header = self.get_header_from_text(s)
        msg_size = header.msg_size
        cr_msg = buf[41: 41+msg_size]
        return header, cr_msg

    def decrypt_recv_msg_body(self, cr_msg, buf_size, pack_key, pin_key, mac_key):
        # with open('b.txt', 'wb') as w:
        #     w.write(cr_msg)
        msg = self.decrypt_msg(cr_msg, pack_key, pin_key)
        # TODO for test
        with open('received_msg.txt', 'wb') as w:
            w.write(msg)

        # b=chardet.detect(msg)
        # print(b)
        data = utils.make_dict_from_xml(msg)
        return data

    def decrypt_msg(self, data, pack_key, pin_key):
        try:
            msg = ab_util.ab_decrypt_msg(data, pack_key)
            # 关键域
            key_fields = self.__class__.__key_fields_set.intersection(set(data.keys()))
            if key_fields:
                data = copy.deepcopy(data)
                for ele in key_fields:
                    if data[ele]:
                        data[ele] = ab_util.ab_decrypt_password(data[ele], pin_key)
            return msg
        except Exception as e:
            print(e)

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = self.check_msg_text_for_common(data, pack_key, pin_key, mac_key)
        return s

    def make_data(self, data, pack_key, pin_key, mac_key, msg_template=None):
        return self.__make_data(data, pack_key, pin_key, mac_key, msg_template)

    def get_code(self, s):
        return '17{}'.format(s)

    def check_mac(self, text, mac, mac_key, pack_key, pin_key):
        # 不检查
        # if not ab_util.check_mac(text, mac, mac_key):
        #     code = self.get_code('2043')
        #     m = {'InstructionCode': self.__class__.trade_no,  # 交易号
        #         'TradeSource': 'B',   # 交易发起方：市场
        #         'InstNo': self.get_mch_id(),   # 市场编号
        #         'Date': self.get_date(),
        #          'Time': self.get_time(),
        #          'Code': code,
        #     }
        #     # t = self.make_data(m, pack_key, pin_key, mac_key)
        #     t = m
        #     return t
        return None

    def check_msg_text_for_common(self, data, pack_key, pin_key, mac_key):
        # 解析错误
        m = None
        if not data:
            code = self.get_code('2044')  # 通讯消息体格式错误
            m = {'InstructionCode': self.__class__.trade_no,  # 交易号
                'TradeSource': self.trade_source,  # 交易发起方
                'InstNo': self.get_mch_id(),  # 市场编号
                'Date': self.get_date(),
                 'Time': self.get_time(),
                 'Code': code,
                 'Info': u'通讯消息体格式错误:'
                 }
        # 缺少必须项
        elif self.must_exist_item and not self.must_exist_item.issubset(set(data.keys())):
            code = self.get_code('2044')
            m = {'InstructionCode': self.__class__.trade_no,  # 交易号
                'TradeSource': self.trade_source,  # 交易发起方
                'InstNo': self.get_mch_id(),  # 市场编号
                'Date': self.get_date(),
                 'Time': self.get_time(),
                 'Code': code,
                 'Info': u'缺少必须项:' + ','.join(self.must_exist_item - set(data.keys()))
                 }
        elif data.get('InstructionCode') != self.trade_no:
            code = '2031'  # 交易码错
            m = {'InstructionCode': self.__class__.trade_no,  # 交易号
                'TradeSource': self.trade_source,   # 交易发起方
                'InstNo': self.get_mch_id(),   # 市场编号
                'Date': self.get_date(),
                 'Time': self.get_time(),
                 'Code': code,
                 'Info': u'交易码错:'
            }
        elif not utils.is_none_or_empty_or_blank(data.get('InstNo')) and data.get('InstNo') != self.get_mch_id():
            code = '2031'  # 市场编码错
            m = {'InstructionCode': self.__class__.trade_no,  # 交易号
                'TradeSource': self.trade_source,   # 交易发起方
                'InstNo': self.get_mch_id(),   # 市场编号
                'Date': self.get_date(),
                 'Time': self.get_time(),
                 'Code': code,
                 'Info': u'市场编码错:'
            }

        if m:
            t = self.make_data(m, pack_key, pin_key, mac_key)
            return t
        return None

    def __make_header(self, msg_size, mac):
        return ab_util.make_header(msg_size, mac=mac,
                                   msg_type=self.__class__.head_msg_type,
                                   trade_no=self.__class__.trade_no,
                                   mch_id=self.__class__.__mch_id)

    def __make_enc_msg(self, data, pack_key, pin_key=None, msg_template=None ):
        key_fields = self.__class__.__key_fields_set.intersection(set(data.keys()))
        if key_fields:
            data = copy.deepcopy(data)
            for ele in key_fields:
                if data[ele]:
                    data[ele] = ab_util.ab_encrypt_password(data[ele], pin_key)
        if not msg_template:
            s = self.__class__.msg_template.decode('utf8').format(**data)
        else:
            s = msg_template.decode('utf8').format(**data)

        s = s.encode('gbk')
        # s = s.encode('utf8')
        with open('r_msg.txt', 'wb') as w:
            w.write(s)
            # w.write(pack_key)
            # w.write(pin_key)
        # logging.exception('test by lwj 11111111111111111')
        # logging.exception('pa_k :'+pack_key)
        # logging.exception('pi_k :'+pin_key)
        c_msg = ab_util.ab_encrypt_msg(s, pack_key)
        return c_msg

    def __make_data(self, data, pack_key, pin_key, mac_key, msg_template=None ):
        c_msg = self.__make_enc_msg(data, pack_key, pin_key,  msg_template)
        mac = ab_util.make_mac(c_msg, mac_key)
        header = self.__make_header(len(c_msg), mac)
        return header + c_msg

    def __check_header_msg(self, header, recv_msg, mac_key):
        mac = header.mac
        if not ab_util.check_mac(recv_msg, mac, mac_key):
            pass # TODO

    def do_event(self, data, keys=None):
        raise NotImplemented