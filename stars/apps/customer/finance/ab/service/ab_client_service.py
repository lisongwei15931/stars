# -*- coding: utf-8 -*-
from __future__ import division

import binascii
import io
import os
from datetime import *

from dateutil import parser

from ab_service import AbService
from stars.apps.customer.finance.ab import ab_util
from stars.apps.customer.finance.ab.ab_client import Client
from stars.apps.customer.finance.utils import FinanceFileSystemStorage


class AbClientService(AbService):
    head_msg_type = 'R'
    trade_source = 'I'
    # trade_no = ''
    # msg_template = ''
    #
    # __mch_id = AgriculturalBankTradeConstData.InstNo
    #
    # __Header = namedtuple('Header', 'api_type ver msg_size head_msg_type trade_no mch_id encryption_flag mac_flag mac reserve')
    # __header_fmt = '!1s3s5s1s5s8s1s1s8s8s'
    #
    # __key_fields_set = {'BankPasswordBankPassword'}

    def __init__(self, suc_handler=None, error_handler=None):
        super(AbClientService, self).__init__(suc_handler, error_handler)
        self.client = Client()

    def send_and_receive(self, data):
        return self.client.send_and_receive(data)

    def send(self, data):
        return self.client.send(data)

    def receive(self, size):
        return self.client.receive(size)

    def receive_all(self):
        buffer = []

        # buf_size = 0
        while True:
            data = self.receive(4096)
            # buf_size += n
            if data:
                buffer.append(data)
            else:
                break
        buf_size = len(buffer) if buffer else 0
        return buffer, buf_size

    def check_msg_text_for_common(self, data, pack_key, pin_key, mac_key):
        # 解析错误
        m = super(AbClientService, self).check_msg_text_for_common(data, pack_key, pin_key, mac_key)

        if m:
            t = self.make_data(m, pack_key, pin_key, mac_key)
            return t

        return None

    def is_successful_result(self, **kwargs):
        return ab_util.is_successful_result_code(kwargs.get('Code'))

    def do_successful_work(self, data, response):
        raise NotImplemented

    def write_log(self, data, response):
        raise NotImplemented

    def do_failed_work(self, data, response):
        if 'Code' in response:
            code = response.get('Code', '')[2:]
        else:
            code = response.get('code', '')[2:]

        if 'Info' in response:
            msg = response.get('Info', '')
        else:
            msg  = response.get('info', '')
        return {'status': {'code': code, 'msg': msg}, 'data': response}

    # 数据检查通过后，做业务相关工作
    def do_work(self, data, response):
        if self.is_successful_result(**response):
            return {'status': {'code': 0, 'msg': u'成功'}, 'data': self.do_successful_work(data, response)}
        else:
            return self.do_failed_work(data, response)

    def make_request_data(self, data):
        raise NotImplemented

    def log(self, data, code):
        # TODO
        pass

    def do_event(self, data, keys=None):

        if not keys:
            pack_key, pin_key, mac_key = self.get_key()
        else:
            pack_key, pin_key, mac_key = keys
            self.pack_key, self.pin_key, self.mac_key = keys

        m = self.make_request_data(data)
        t = self.make_data(m, pack_key, pin_key, mac_key)
        with open('send_buf.txt', 'wb') as w:
            w.write(t)
        buf, buf_size = self.send_and_receive(t)
        with open('received_buf.txt', 'wb') as w:
            w.writelines(buf)
        if buf_size == 0:
            # error
            self.log(data, code=-1)
        header, cr_msg = self.split_header_msg(buf)
        # with open('c_msg.txt', 'wb') as w:
        #     w.write(cr_msg)
        assert(header.trade_no == self.trade_no)

        # 不实现 by 农行赵工
        # # 检查mac
        # s = self.check_mac(cr_msg, header.mac, mac_key, pack_key, pin_key)
        # if s:
        #     print('error mac')

            # return self.send(s)

        msg_text = self.decrypt_recv_msg_body(cr_msg, len(cr_msg), pack_key, pin_key, mac_key)

        s = self.check_msg_text(msg_text, pack_key, pin_key, mac_key)
        if s:
            return self.send_and_receive(s)

        #检查通过
        return self.do_work(m, response=msg_text)


    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


class TransferKeyClientService(AbClientService):
    head_msg_type = 'R'
    trade_no = '10009'
    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
        }
        return m

    def do_work(self, data, response):
        if self.is_successful_result(**response):
            return self.do_successful_work(data, response)
            # return
        else:
            self.do_failed_work()

    def do_successful_work(self, data, response):
        pack_key = binascii.unhexlify(response['PagKey'])
        pin_key = binascii.unhexlify(response['PinKey'])
        mac_key = binascii.unhexlify(response['MacKey'])

        o_pack_key, o_pin_key, o_mac_key = ab_util.get_ori_key()
        pack_key = ab_util.ab_decrypt_msg(pack_key, o_pack_key)
        pin_key = ab_util.ab_decrypt_msg(pin_key, o_pin_key)

        mac_key = ab_util.ab_decrypt_msg(mac_key, o_mac_key)
        # mac_key = ab_util.

        # resp = ConfirmTransferKeyClientService().do_event(data=None, keys=(pack_key, pik_key, mac_key))
        # 
        # if self.is_successful_result(**resp):
        #     ab_util.set_key(pack_key, pik_key, mac_key)
        pack_key = pack_key.rstrip('\0')
        pin_key = pin_key.rstrip('\0')
        mac_key = mac_key.rstrip('\0')
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'pack_key': pack_key,
            'pin_key': pin_key,
            'mac_key': mac_key,
             }
        # return (pack_key, pin_key, mac_key)
        return m

    def write_log(self, data, response):
        pass


    def do_failed_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)


class ConfirmTransferKeyClientService(AbClientService):
    head_msg_type = 'R'
    trade_no = '10010' # 交易号：密钥交换确认
    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                     '<Contract><BankPassword>{BankPassword}</BankPassword></Contract>' \
                    '</root>'

    __BANK_PASSWORD = '111111'

    def __init__(self, client=None, suc_handler=None, error_handler=None):
        super(AbClientService, self).__init__(suc_handler, error_handler)
        if client:
            self.client = client
            self.__is_shared_client = True
        else:
            self.client = Client()
            self.__is_shared_client = False


    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'BankPassword': self.__BANK_PASSWORD,
        }
        return m

    def do_work(self, data, response):
        if self.is_successful_result(**response):
            return self.do_successful_work(data, response)
            # return
        else:
            self.do_failed_work()
        # return response

    def do_successful_work(self, data, response):
        # if self.is_successful_result(**resp):
        #     if self.pack_key or self.pin_key or self.mac_key:
        expired_date = response.get('KeyExpiryDate')
        if not expired_date or expired_date == '99999999':
            expired_date = datetime(year=9999,month=1,day=1).date()
        else:
            try:
                expired_date = parser.parse(expired_date)
            except Exception as e:
                expired_date = datetime.now().date()+timedelta(days=1)

        ab_util.set_key(self.pack_key, self.pin_key, self.mac_key, expired_date)
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'pack_key': self.pack_key,
            'pin_key': self.pin_key,
            'mac_key': self.mac_key,
            'expired_date': response.get('KeyExpiryDate'),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)

    def close(self):
        if not self.__is_shared_client:
            super(self.__class__, self).close()


class MarketSignInClientService(AbClientService):
    __msg_type = 'R'
    trade_no = '10001'  # 交易号：市场签到
    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                   '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date() ,
             'Time': self.get_time(),
        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'busi_type': response.get('BusiType', ''),
            'money_kind': response.get('MoneyKind', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'busi_type': response.get('BusiType', ''),
            'money_kind': response.get('MoneyKind', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)


class MarketSignOutClientService(AbClientService):
    head_msg_type = 'R'
    trade_no = '10002'  # 交易号：市场签退
    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                     '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'busi_type': response.get('BusiType', ''),
            'money_kind': response.get('MoneyKind', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'busi_type': response.get('BusiType', ''),
            'money_kind': response.get('MoneyKind', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)


# 4.2.2.3.上传/下载文件BCD_IO_INST_012
class MarketUploadDownloadFileClientService(AbClientService):
    head_msg_type = 'R'
    trade_no = '10008'  # 交易号：市场上传/下载文件

    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                        '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                       '<FileName></FileName><FileSize></FileSize>' \
                   '</pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                   '<Contract>' \
                    '<UpDownFlag>{UpDownFlag}</UpDownFlag>' \
                   '</Contract>' \
                    '</root>'
    up_down_flag = ''
    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'UpDownFlag': self.__class__.up_down_flag,
        }
        return m


# 4.2.2.3.上传文件BCD_IO_INST_012
#存管模式有上传，转账模式无上传
#存管模式：
# 市场上传的清算文件	iBusi_$.YYYYMMDD	会员业务文件	客户日终上送的当日非出入金资金发生流水，同一类型的变动扎差为一条记录
# 	iBala_$.YYYYMMDD	会员资金余额文件	客户清算后余额
# 	iPay_$.YYYYMMDD	机构交收文件	　
# 	iBalaTail_$.YYYYMMDD	会员资金明细	用以向会员展示期末余额明细
# 银行清算结果文件	bBalaErr_$.YYYYMMDD	余额不符文件	　
class MarketUploadFileClientService(MarketUploadDownloadFileClientService):
    if False:  # 不实现
        up_down_flag = 'U'

        def do_event(self, data, keys=None):

            if not keys:
                pack_key, pin_key, mac_key = self.get_key()
            else:
                pack_key, pin_key, mac_key = keys
                self.pack_key, self.pin_key, self.mac_key = keys

            m = self.make_request_data(data)
            t = self.make_data(m, pack_key, pin_key, mac_key)
            with open('send_buf.txt', 'wb') as w:
                w.write(t)
            self.send(t)

            file_name = data['file_name']
            try:
                file_name_size = len(file_name.encode('gbk'))
            except Exception:
                file_name_size = len(file_name)

            upload_file_name = data['local_file_path']
            file_size = os.path.getsize(upload_file_name)

            # s = '{:0>3}{:0>8}'.format(file_name_size, file_size)
            s1 = '{:0>3}'.format(file_name_size)
            self.send(s1)
            self.send(file_name)
            s2 = '{:0>8}'.format(file_size)
            self.send(s2)

            # self.send('{:0>8}'.format(file_size))
            b = self.receive(8)
            # c = self.receive(10)
            # b, _ = self.receive_all()
            # if b != '0000':  # 接收确认失败
            #     # TODO
            #     self.log(data={}, code=-1)
            #     header, cr_msg = self.split_header_msg(b)
            #     msg_text = self.decrypt_recv_msg_body(cr_msg, len(cr_msg), pack_key, pin_key, mac_key)



            # with open('received_buf.txt', 'wb') as w:
            # 接收文件
            with open(upload_file_name, 'rb') as r:
                c = r.read(4096-8)
                if c:
                    self.send('{:0>8}'.format(len(c))+c)

            # 接收响应报文
            buf, buf_size  = self.receive_all()
            header, cr_msg = self.split_header_msg(buf)
            # with open('c_msg.txt', 'wb') as w:
            #     w.write(cr_msg)
            assert(header.trade_no == self.trade_no)

            # 不实现 by 农行赵工
            # # 检查mac
            # s = self.check_mac(cr_msg, header.mac, mac_key, pack_key, pin_key)
            # if s:
            #     print('error mac')

                # return self.send(s)

            msg_text = self.decrypt_recv_msg_body(cr_msg, len(cr_msg), pack_key, pin_key, mac_key)

            s = self.check_msg_text(msg_text, pack_key, pin_key, mac_key)
            if s:
                return self.send_and_receive(s)

            #检查通过
            return self.do_work(m, response=msg_text)
        def do_work(self, data, response):
            if self.is_successful_result(**response):
                # TODO
                return {'status': {'code': 0, 'msg': u'成功'}, 'data': self.do_successful_work(data, response)}
            else:
                return {'status': self.do_failed_work(data, response)}

        def do_successful_work(self, data, response):
            pass

        def write_log(self, data, response):
            pass

        def do_failed_work(self, data, response):
            return super(self.__class__, self).do_failed_work(data, response)


# 4.2.2.3.下载文件BCD_IO_INST_012
#转账模式只有如下文件：银行下发对账文件
# bTransfer_$.YYYYMMDD	出入金对账文件	　
# 	bAccEdit_$.YYYYMMDD	客户信息变动文件	　
# 	bInfo_$.YYYYMMDD	客户信息文件	　
#存管模式除上述文件外，还有：
# 银行清算结果文件	bBalaErr_$.YYYYMMDD	余额不符文件	　
# 	bZfph_$.YYYYMMDD	总分平衡文件	　
# 	bBala_$.YYYYMMDD	银行资金文件	完成清算后，所有会员本日期末余额
class MarketDownloadFileClientService(MarketUploadDownloadFileClientService):
    up_down_flag = 'D'

    def do_event(self, data, keys=None):

        if not keys:
            pack_key, pin_key, mac_key = self.get_key()
        else:
            pack_key, pin_key, mac_key = keys
            self.pack_key, self.pin_key, self.mac_key = keys

        m = self.make_request_data(data)
        t = self.make_data(m, pack_key, pin_key, mac_key)
        with open('send_buf.txt', 'wb') as w:
            w.write(t)
        self.send(t)

        file_name = data['file_name']
        try:
            file_name_size = len(file_name.encode('gbk'))
        except Exception:
            file_name_size = len(file_name)

        a = self.send('{:0>3}'.format(file_name_size))  # 文件名长度为3字节
        self.send(file_name)
        file_size = self.receive(8)
        file_size = int(file_size)
        self.client.send('0000')
        m['file_size'] = file_size
        received_size = 0

        if file_size > 0:
            save_file_path = data['save_file_path']

            # with open('received_buf.txt', 'wb') as w:
            # 接收文件
            # directory = os.path.dirname(save_file_path)
            # if not os.path.exists(directory):
            #     os.makedirs(directory)
            with io.BytesIO() as b:
                while True:
                    pack_data_size = int(self.receive(8))
                    pack_data = self.receive(pack_data_size)
                    if pack_data:
                        b.write(pack_data)
                        self.send('0000')
                    else:
                        break
                    received_size += pack_data_size
                    if received_size >= file_size:
                        break
                st = FinanceFileSystemStorage(the_day=data['the_day'])
                name = st.save(file_name, b)
                m['save_file_path'] = st.path(name)

            # with open(save_file_path, 'wb') as ws:
            #     while True:
            #         pack_data_size = int(self.receive(8))
            #         pack_data = self.receive(pack_data_size)
            #         if pack_data:
            #             ws.write(pack_data)
            #             self.send('0000')
            #         else:
            #             break
            #         received_size += pack_data_size
            #         if received_size >= file_size:
            #             break

        m['received_size'] = received_size

        # 接收响应报文
        buf, buf_size  = self.receive_all()
        header, cr_msg = self.split_header_msg(buf)
        with open('c_msg.txt', 'wb') as w:
            w.write(cr_msg)
        assert(header.trade_no == self.trade_no)

        msg_text = self.decrypt_recv_msg_body(cr_msg, len(cr_msg), pack_key, pin_key, mac_key)

        s = self.check_msg_text(msg_text, pack_key, pin_key, mac_key)
        if s:
            return self.send_and_receive(s)

        #检查通过
        return self.do_work(m, response=msg_text)

    def do_work(self, data, response):
        if self.is_successful_result(**response):
            # TODO
            return {'status': {'code': 0, 'msg': u'成功'}, 'data': self.do_successful_work(data, response)}
        else:
            return {'status': self.do_failed_work(data, response)}

    def do_successful_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'file_name': data['file_name'],
            'saved_file_path': data['saved_file_path'],
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'file_name': data['file_name'],
             }
        return super(self.__class__, self).do_failed_work(data, m)


class MarketCloseClientService(AbClientService):
    head_msg_type = 'R'
    trade_no = '13011'  # 交易号：闭市

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                     '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'busi_type': response.get('BusiType', ''),
            'money_kind': response.get('MoneyKind', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        m = {
             'serial_no': response.get('SerialNo', ''),
             'inst_serial': response['InstSerial'],
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'busi_type': response.get('BusiType', ''),
            'money_kind': response.get('MoneyKind', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)


class MarketSignContractService(AbClientService):
    head_msg_type = 'R'
    trade_no = '11001'  # 交易号：签约
    # CashExCode 1-汇；2-钞
    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business>' \
                       '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
                       '<CashExCode>2</CashExCode>' \
                   '</Business>' \
                     '<Contract>' \
                        '<BankAccount>{BankAccount}</BankAccount>' \
                        '<BankPassword>{BankPassword}</BankPassword>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<InstBranch>{InstBranch}</InstBranch><InstBranchName></InstBranchName>' \
                        '<HavePwd>{HavePwd}</HavePwd>' \
                        '<TradePassword>{TradePassword}</TradePassword>' \
                        '<InstFundBala></InstFundBala>' \
                     '</Contract>' \
                     '<Transfer><TransferLimit>{TransferLimit}</TransferLimit></Transfer>' \
                     '<Client>' \
                        '<CertType>{CertType}</CertType>' \
                        '<CertID>{CertID}</CertID>' \
                        '<ClientName>{ClientName}</ClientName>' \
                        '<ClientKind>{ClientKind}</ClientKind>' \
                        '<Gender>{Gender}</Gender>' \
                        '<Nationality>CHN</Nationality>' \
                        '<TelNo>{TelNo}</TelNo>' \
                        '<FaxNo>{FaxNo}</FaxNo>' \
                        '<MobiNo>{MobiNo}</MobiNo>' \
                        '<PostCode>{PostCode}</PostCode>' \
                        '<Address>{Address}</Address>' \
                        '<Email>{Email}</Email>' \
                     '</Client>' \
                    '<Agent>' \
                        '<AgentName></AgentName>' \
                        '<AgentCertType></AgentCertType>' \
                        '<AgentCertID></AgentCertID>' \
                        '<AgentGender></AgentGender>' \
                        '<AgentNationality></AgentNationality>' \
                        '<AgentTelephone></AgentTelephone>' \
                        '<AgentFax></AgentFax>' \
                        '<AgentMobile></AgentMobile>' \
                        '<AgentPostcode></AgentPostcode>' \
                        '<AgentAddress></AgentAddress>' \
                        '<AgentEmail></AgentEmail>' \
                   '</Agent>' \
                   '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

        # Gender	性别
        # Nationality	国籍或地区
        # TelNo 	电话号码
        # FaxNo	传真
        # MobiNo	手机
        # PostCode	邮政编码
        # Address	客户地址
        # Email	电子邮件
        # AgentName	经办人姓名
        # AgentCertType	经办人证件类型
        # AgentCertID	经办人证件号码
        # AgentGender	经办人性别
        # AgentNationality	经办人国籍
        # AgentTelephone	经办人电话
        # AgentFax	经办人传真
        # AgentMobile	经办人手机
        # AgentPostcode	经办人邮政编码
        # AgentAddress	经办人通信地址
        # AgentEmail	经办人电子邮件
        # Reserve1	保留字段1
        # Reserve2	保留字段2
    # '<ClientKind>{ClientKind}</ClientKind>' \   客户性质
    #  '<TradePassword>{TradePassword}</TradePassword>' \ 出入金密码	☆	对公账户必须设定
    # '<HavePwd>{HavePwd}</HavePwd>'   是否留密	☆	对公账户必须设定1
    # ClientKind:0，个人；1：机构
    # TransferLimit：转账限额。0：无限制
    # 返回值中有ClientNo，为签约时银行生成
    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'BankAccount': data['bank_account'],
            'BankPassword': data.get('bank_password', ''),
            'ClientName': data['client_name'],
            'InstFundAcc': data['inst_fund_acc'],
            'InstBranch': data['inst_branch'],
            'TransferLimit': data['transfer_limit'],
            'CertID': data['cert_id'],
             'CertType': data['cert_type'],
             'HavePwd': data.get('have_pwd', ''),
             'TradePassword': data.get('trade_password', ''),
             'ClientKind': data.get('client_kind', ''),
             'Gender': data.get('gender', ''),

             'TelNo': data.get('tel_no', ''),
             'FaxNo': data.get('fax_no', ''),
             'MobiNo': data.get('mobile', ''),
             'PostCode': data.get('post_code', ''),
             'Address': data.get('address', ''),
             'Email': data.get('email', ''),

        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'summary': response.get('Summary', ''),
             'code': response['Code'],
             'info': response['Info'],
             'cert_id': response['CertID'],
             'cert_type': response['CertType'],
            'trade_source': response.get('TradeSource', ''),
            'serial_no': response['SerialNo'],
             'inst_serial': response['InstSerial'],
            'client_no': response['ClientNo'],
            'bank_account': response.get('BankAccount', ''),
            'inst_fund_acc': response['InstFundAcc'],
             'inst_fund_bala': response.get('InstFundBala', ''),
            'client_name': response['ClientName'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
            'reserve1': response.get('Reserve1', ''),
            'reserve2': response.get('Reserve2', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        # 4026 保证金账户不正确
        # BEER 卡号不合法或不存在、客户姓名不符、证件号不符
        # 5010 出入金关系已经存在
        m = {'bank_account': response['BankAccount'],
             'client_no': response['ClientNo'],
             'serial_no': response['SerialNo'],
             'summary': response.get('Summary', ''),
             'code': response['Code'],
             'info': response['Info'],
             'inst_fund_acc': response['InstFundAcc'],
             'cert_id': response['CertID'],
             'inst_serial': response['InstSerial'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'response': response,
             }
        return super(self.__class__, self).do_failed_work(data, m)


# 解约
class RescindContractService(AbClientService):
    head_msg_type = 'R'
    trade_no = '11004'  # 交易号：解约

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                     '<Contract>' \
                        '<BankAccount>{BankAccount}</BankAccount>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<ClientNo>{ClientNo}</ClientNo>' \
                     '</Contract>' \
                     '<Client>' \
                        '<CertType>{CertType}</CertType>' \
                        '<CertID>{CertID}</CertID>' \
                        '<ClientName>{ClientName}</ClientName>' \
                     '</Client>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
            'BankAccount': data.get('bank_account' ,''),
            'ClientName': data['client_name'],
            'InstFundAcc': data['inst_fund_acc'],
            'CertID': data['cert_id'],
             'ClientNo': data['client_no'],
             'CertType': data['cert_type'],
        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'code': response['Code'],
             'info': response.get('Info', ''),
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'serial_no': response['SerialNo'],
             'inst_serial': response['InstSerial'],
             'trade_source': response.get('TradeSource', ''),
            'client_no': response['ClientNo'],
            'bank_account': response.get('BankAccount', ''),
            'inst_fund_acc': response['InstFundAcc'],
            'client_name': response['ClientName'],
             'summary': response.get('Summary', ''),
             'cert_id': response['CertID'],
             'cert_type': response['CertType'],
            'reserve1': response.get('Reserve1', ''),
            'reserve2': response.get('Reserve2', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        # 5052 当日有出入金不允许解约/换卡/强制变更银行账户
        m = {'bank_account': response['BankAccount'],
             'client_no': response['ClientNo'],
             'serial_no': response['SerialNo'],
             'summary': response.get('Summary', ''),
             'code': response['Code'],
             'info': response['Info'],
             'inst_fund_acc': response['InstFundAcc'],
             'cert_id': response['CertID'],
             'inst_serial': response['InstSerial'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'response': response,
             }
        return super(self.__class__, self).do_failed_work(data, m)


# 出金（提现）
class WithdrawService(AbClientService):
    head_msg_type = 'R'
    trade_no = '12002'  # 交易号：出金

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                   '<Business>' \
                       '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
                       '<CashExCode>2</CashExCode>' \
                   '</Business>' \
                     '<Contract>' \
                        '<BankAccount>{BankAccount}</BankAccount><BankPassword>{BankPassword}</BankPassword>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<ClientNo>{ClientNo}</ClientNo>' \
                        '<TradePassword>{TradePassword}</TradePassword>' \
                        '<SettleAcc></SettleAcc>' \
                        '<AccName></AccName>' \
                     '</Contract>' \
                    '<Transfer>' \
                       '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                       '<Taster></Taster>' \
                       '<Broker></Broker>' \
                       '<InstRatifier></InstRatifier>' \
                   '</Transfer>' \
                     '<Client>' \
                        '<ClientName>{ClientName}</ClientName>' \
                     '</Client>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'BankPassword': data.get('bank_password', ''),
             'ClientNo': data['client_no'],
             'TransferAmount': data['transfer_amount'],
             'InstFundAcc': data['inst_fund_acc'],
             'ClientName': data['client_name'],
             'BankAccount': data.get('bank_account', ''),
             'TradePassword': data.get('trade_password', ''),
        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'client_no': response['ClientNo'],
             'inst_fund_acc': response['InstFundAcc'],
             'serial_no': response['SerialNo'],
             'inst_serial': response['InstSerial'],
             'host_serial': response['HostSerial'],
             'transfer_amount': response['TransferAmount'],
             'enable_bala': response.get('EnableBala', ''),
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'money_usage': response.get('MoneyUsage', ''),
             'money_usage_info': response.get('MoneyUsageInfo', ''),
            'instruction_code': response.get('InstructionCode', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        ## 4001 导入xml报文失败
        m = {
             'client_no': response['ClientNo'],
             'inst_fund_acc': response['InstFundAcc'],
             'serial_no': response['SerialNo'],
             'inst_serial': response['InstSerial'],
             'host_serial': response['HostSerial'],
             'transfer_amount': response['TransferAmount'],
             'enable_bala': response.get('EnableBala', ''),
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'money_usage': response.get('MoneyUsage', ''),
             'money_usage_info': response.get('MoneyUsageInfo', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)


# 入金(充值）
class RechargeService(AbClientService):
    head_msg_type = 'R'
    trade_no = '12001'  # 交易号：入金

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business>' \
                       '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
                       '<CashExCode>2</CashExCode>' \
                   '</Business>' \
                     '<Contract>' \
                        '<BankAccount>{BankAccount}</BankAccount>' \
                        '<BankPassword>{BankPassword}</BankPassword>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<ClientNo>{ClientNo}</ClientNo>' \
                        '<AccName></AccName><SettleAcc></SettleAcc>' \
                   '<TradePassword>{TradePassword}</TradePassword>' \
                     '</Contract>' \
                     '<Transfer>' \
                       '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                       '<Taster></Taster>' \
                       '<Broker></Broker>' \
                       '<InstRatifier></InstRatifier>' \
                   '</Transfer>' \
                     '<Client>' \
                        '<ClientName>{ClientName}</ClientName>' \
                     '</Client>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'BankPassword': data.get('bank_password', ''),
             'ClientNo': data['client_no'],
             'TransferAmount': data['transfer_amount'],
             'InstFundAcc': data['inst_fund_acc'],
             'ClientName': data['client_name'],
             'BankAccount': data.get('bank_account', ''),
             'TradePassword': data.get('trade_password', ''),
        }
        return m

    def do_successful_work(self, data, response):
        m = {
             'client_no': response['ClientNo'],
             'inst_fund_acc': response['InstFundAcc'],
             'serial_no': response['SerialNo'],
             'inst_serial': response['InstSerial'],
             'host_serial': response['HostSerial'],
             'transfer_amount': response['TransferAmount'],
             'enable_bala': response.get('EnableBala', ''),
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'money_usage': response.get('MoneyUsage', ''),
             'money_usage_info': response.get('MoneyUsageInfo', ''),
            'instruction_code': response.get('InstructionCode', ''),
             }
        return m

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        ## 4001 导入xml报文失败
        m = {
             'client_no': response['ClientNo'],
             'inst_fund_acc': response['InstFundAcc'],
             'serial_no': response['SerialNo'],
             'inst_serial': response['InstSerial'],
             'host_serial': response['HostSerial'],
             'transfer_amount': response['TransferAmount'],
             'enable_bala': response.get('EnableBala', ''),
             'code': response['Code'],
             'info': response['Info'],
             'date': response.get('Date', ''),
             'time': response.get('Time', ''),
             'money_usage': response.get('MoneyUsage', ''),
             'money_usage_info': response.get('MoneyUsageInfo', ''),
             }
        return super(self.__class__, self).do_failed_work(data, m)


# 冲出金
class CancelWithdrawService(AbClientService):
    head_msg_type = 'R'
    trade_no = '12004'  # 交易号：冲出金

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial>' \
                        '<InstSerial>{InstSerial}</InstSerial>' \
                        '<CancelInstSerial>{CancelInstSerial}</CancelInstSerial>' \
                   '</Serial>' \
                   '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                     '<Contract>' \
                        '<BankAccount>{BankAccount}</BankAccount><BankPassword>{BankPassword}</BankPassword>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<ClientNo>{ClientNo}</ClientNo>' \
                     '</Contract>' \
                     '<Transfer><TransferAmount>{TransferAmount}</TransferAmount></Transfer>' \
                     '<Client>' \
                        '<ClientName>{ClientName}</ClientName>' \
                     '</Client>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
        }
        return m

    def do_successful_work(self, data, response):
        pass

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        return super(self.__class__, self).do_failed_work(data, response)


# 冲入金
class CancelRechargeService(AbClientService):
    head_msg_type = 'R'
    trade_no = '12003'  # 交易号：冲入金

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial>' \
                        '<InstSerial>{InstSerial}</InstSerial>' \
                        '<CancelInstSerial>{CancelInstSerial}</CancelInstSerial>' \
                   '</Serial>' \
                   '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                     '<Contract' \
                        '<BankAccount>{BankAccount}</BankAccount><BankPassword>{BankPassword}</BankPassword>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<ClientNo>{ClientNo}</ClientNo>' \
                     '</Contract>' \
                     '<Transfer><TransferAmount>{TransferAmount}</TransferAmount></Transfer>' \
                     '<Client>' \
                        '<ClientName>{ClientName}</ClientName>' \
                     '</Client>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
        }
        return m

    def do_successful_work(self, data, response):
        pass

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        return super(self.__class__, self).do_failed_work(data, response)


# 出金审核通知
class WithdrawAuditingInformService(AbClientService):
    head_msg_type = 'R'
    trade_no = '12006'  # 交易号：出金审核通知

    msg_template = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                        '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                        '<OriSerial>{OriSerial}</OriSerial>' \
                   '</pub>' \
                    '<Serial>' \
                        '<InstSerial>{InstSerial}</InstSerial>' \
                   '</Serial>' \
                    '<Business>' \
                        '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
                        '<CashExCode>{CashExCode}</CashExCode>' \
                    '</Business>' \
                     '<Contract>' \
                        '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<ClientNo>{ClientNo}</ClientNo>' \
                     '</Contract>' \
                     '<Transfer>' \
                        '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                        '<AuditRet>{AuditRet}</AuditRet>' \
                         '<Taster></Taster>' \
                       '<Broker></Broker>' \
                       '<InstRatifier></InstRatifier>' \
                    '</Transfer>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'AuditRet': data['audit_ret'], # 0-通过，R-拒绝, P-暂缓
             'TransferAmount': data['transfer_amount'],
             'OriSerial': data['ori_serial'], # 原交易流水号
             'InstFundAcc': data['inst_fund_acc'],
             'ClientNo': data['client_no'],
             'CashExCode': data.get('cash_ex_code', ''),
        }
        return m

    def do_successful_work(self, data, response):
        pass

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        return super(self.__class__, self).do_failed_work(data, response)


# 出入金流水查询
# 该交易为市场提供批量查询其当日所有客户发起的出入金日间流水的功能，和单个客户当日所有渠道出入金日间流水查询
# 单个用户查询需要inst_fund_acc、client_no，多个查询为空----字段需要存在，不然报错：解包错
class RechargeWithdrawHistoryQueryService(AbClientService):
    head_msg_type = 'R'
    trade_no = '13003'  # 交易号：出入金流水查询

    msg_template = '<root>' \
                       '<pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                            '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                            '<TradeSource>{TradeSource}</TradeSource>' \
                            '<InstNo>{InstNo}</InstNo>' \
                            '<PostionStr>{PostionStr}</PostionStr><RequestNum>{RequestNum}</RequestNum>' \
                       '</pub>' \
                        '<Serial>' \
                            '<InstSerial>{InstSerial}</InstSerial>' \
                       '</Serial>' \
                        '<Business><BusiType>6</BusiType><MoneyKind>01</MoneyKind></Business>' \
                        '<Contract>' \
                            '<BankAccount>{BankAccount}</BankAccount>' \
                            '<InstBranch>{InstBranch}</InstBranch>' \
                            '<Summary>{Summary}</Summary>'\
                                '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                                '<ClientNo>{ClientNo}</ClientNo>' \
                        '</Contract>'\
                    '</root>'
    __single_account_text = '<Contract>' \
                                '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                                '<ClientNo>{ClientNo}</ClientNo>' \
                            '</Contract>'
    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'PostionStr': 0 if not data else data.get('position', 0),
             'RequestNum': 10 if not data else data.get('request_num', 10),
             'InstFundAcc': '' if not data else data.get('inst_fund_acc', ''),
             'ClientNo': '' if not data else data.get('client_no', ''),
             'BankAccount': '' if not data else data.get('bank_account', ''),
             'InstBranch': '' if not data else data.get('inst_branch', ''),
             'Summary': '' if not data else data.get('summary', ''),
        }

        # if data is not None and data.get('inst_fund_acc'):
        #     self.msg_template = self.__class__.msg_template.replace('-single_account-', self.__class__.__single_account_text, 1)
        #     m['InstFundAcc'] = data['inst_fund_acc']
        #     m['ClientNo'] = data.get('client_no', '')
        # else:
        #     self.msg_template = self.__class__.msg_template.replace('-single_account-', '', 1)

        return m

    def make_data(self, data, pack_key, pin_key, mac_key, msg_template=None):

        return super(self.__class__, self).make_data(data, pack_key,pin_key, mac_key, self.msg_template)

    def do_successful_work(self, data, response):
        pass

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        return super(self.__class__, self).do_failed_work(data, response)


# 单笔出入金流水查询
class RechargeWithdrawStatusSingleQueryService(AbClientService):
    head_msg_type = 'R'
    trade_no = '13004'  # 交易号：单笔出入金流水查询

    msg_template = '<root>' \
                       '<pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                            '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                            '<TradeSource>{TradeSource}</TradeSource>' \
                            '<InstNo>{InstNo}</InstNo>' \
                       '</pub>' \
                        '<Serial>' \
                            '<InstSerial>{InstSerial}</InstSerial>' \
                            '<CorrectSerial>{CorrectSerial}</CorrectSerial>' \
                       '</Serial>' \
                        '<Business>' \
                            '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
                            '<CashExCode></CashExCode>' \
                        '</Business>' \
                         '<Contract>' \
                            '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                            '<ClientNo></ClientNo>' \
                            '<BankAccount></BankAccount>' \
                            '<SettleAcc></SettleAcc>' \
                         '</Contract>' \
                         '<Transfer>' \
                            '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '</Transfer>' \
                        '<Client>' \
                            '<CertType></CertType>' \
                            '<CertID></CertID>' \
                         '</Client>' \
                    '</root>'
         #CashExCode 1:汇 2：钞
                            #
    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': data['inst_serial'],  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data['transfer_amount'],
             'InstFundAcc': data['inst_fund_acc'],
             'CorrectSerial': data['original_serial'],
             # 'ClientNo': data['client_no'],
        }
        return m

    def do_successful_work(self, data, response):
        pass

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        return super(self.__class__, self).do_failed_work(data, response)


# 查询账户余额
class AccountBalanceQueryService(AbClientService):
    head_msg_type = 'R'
    trade_no = '11009'  # 交易号：查询账户余额

    msg_template = '<root>' \
                       '<pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                            '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                            '<TradeSource>{TradeSource}</TradeSource>' \
                            '<InstNo>{InstNo}</InstNo>' \
                       '</pub>' \
                        '<Serial>' \
                            '<InstSerial>{InstSerial}</InstSerial>' \
                       '</Serial>' \
                        '<Business>' \
                           '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
                           '<CashExCode></CashExCode>' \
                       '</Business>' \
                         '<Contract>' \
                            '<BankAccount>{BankAccount}</BankAccount><BankPassword>{BankPassword}</BankPassword>' \
                            '<InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                            '<ClientNo>{ClientNo}</ClientNo>' \
                         '</Contract>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'BankAccount': data['bank_account'],
             'BankPassword': data['bank_password'],  # 对公账户值为出入金密码（TradePassword)
             'ClientNo': data['client_no'],
             'InstFundAcc': data['inst_fund_acc'],
        }
        return m

    def do_successful_work(self, data, response):
        fetch_balance = response['FetchBalance']
        enable_balance = response['EnableBalance']
        return {'fetch_balance': fetch_balance,
                'enable_balance': enable_balance}

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        m = {'5009': u'出入金关系不存在'}
        return super(self.__class__, self).do_failed_work(data, response)


# 不需要
# # 市场清算确认通知
# class MarketSettlementInformService(AbClientService):
#     head_msg_type = 'R'
#     trade_no = '13019'  # 交易号：市场清算确认通知
#
#     msg_template = '<root>' \
#                        '<pub><InstructionCode>{InstructionCode}</InstructionCode>' \
#                             '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
#                             '<TradeSource>{TradeSource}</TradeSource>' \
#                             '<InstNo>{InstNo}</InstNo>' \
#                        '</pub>' \
#                         '<Serial>' \
#                             '<InstSerial>{InstSerial}</InstSerial>' \
#                        '</Serial>' \
#                          '<Business>' \
#                             '<BusiType>6</BusiType><MoneyKind>01</MoneyKind>' \
#                          '</Business>' \
#                     '</root>'
#
#     def make_request_data(self, data):
#         m = {'InstructionCode': self.__class__.trade_no,
#             'EntrustWay': 'I',  # 委托方式： 市场
#             'TradeSource': 'I',   # 交易发起方：市场
#             'InstNo': self.get_mch_id(),   # 市场编号
#             'InstSerial': ab_util.create_ab_inst_serial(ab_util.get_service_name_for_ab(self.get_trade_no())),  # 市场流水号
#             'Date': self.get_date(),
#              'Time': self.get_time(),
#         }
#         return m
#
#     def do_successful_work(self, data, response):
#         pass
#
#     def write_log(self, data, response):
#         pass
#
#     def do_failed_work(self, data, response):
#         return super(self.__class__, self).do_failed_work(data, response)


# 个人身份认证
class IdAuthenticationService(AbClientService):
    head_msg_type = 'R'
    trade_no = '14001'  # 交易号：个人身份认证

    msg_template = '<root>' \
                       '<pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                            '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                            '<TradeSource>{TradeSource}</TradeSource>' \
                            '<InstNo>{InstNo}</InstNo>' \
                       '</pub>' \
                        '<Serial>' \
                            '<InstSerial>{InstSerial}</InstSerial>' \
                       '</Serial>' \
                        '<RESERVE><Reserve1></Reserve1></RESERVE>' \
                         '<Client>' \
                            '<CertType>{CertType}</CertType>' \
                            '<CertID>{CertID}</CertID>' \
                            '<ClientName>{ClientName}</ClientName>' \
                         '</Client>' \
                        '<Contract>' \
                            '<BankAccount>{BankAccount}</BankAccount>' \
                        '</Contract>' \
                    '</root>'

    def make_request_data(self, data):
        m = {'InstructionCode': self.__class__.trade_no,
            'EntrustWay': 'I',  # 委托方式： 市场
            'TradeSource': 'I',   # 交易发起方：市场
            'InstNo': self.get_mch_id(),   # 市场编号
            'InstSerial': self.create_ab_inst_serial(),  # 市场流水号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'CertID': data['id'],
             'CertType': data.get('cert_type', '110001'),
             'ClientName': data['name'],
             'BankAccount': data['bank_account'],
        }
        return m

    def do_successful_work(self, data, response):
        pass

    def write_log(self, data, response):
        pass

    def do_failed_work(self, data, response):
        return super(self.__class__, self).do_failed_work(data, response)
