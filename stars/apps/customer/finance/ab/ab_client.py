# encoding: utf-8

import socket
import time

__TEST__ = False


class Client(object):
    def __init__(self):
        self.__conn = self.__get_connection()

    def __get_connection(self ):
        global s
        if __TEST__:
            AB_SERVER_IP = '127.0.0.1'
            AB_SERVER_PORT = 8010
        else:
            AB_SERVER_IP = '202.108.144.31'
            AB_SERVER_PORT = 3411
        SERVER_URL = (AB_SERVER_IP, AB_SERVER_PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(5):
            try:
                s.connect(SERVER_URL)
                break
            except Exception, e:
                time.sleep(0.1)
                continue
        return s

    def send(self, data):
        self.__conn.sendall(data)

    def receive(self, size):
        return self.__conn.recv(size)

    def send_and_receive(self, data):
        self.__conn.sendall(data)
        buffer = []

        # buf_size = 0
        while True:
            data = self.__conn.recv(4096)
            # buf_size += n
            if data:
                buffer.append(data)
            else:
                break
        buf_size = len(buffer) if buffer else 0
        return buffer, buf_size

    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


def send(data):
    with Client() as c:
        return c.send_and_receive(data)


# def confirm_transfer_key(new_pack_key, new_pin_key, new_mac_key):
#     s = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
#         '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
#         '<TradeSource>{TradeSource}</TradeSource>' \
#         '<InstNo>{InstNo}</InstNo></pub>' \
#         '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
#         '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business>' \
#         '</root>'
#     inst_code = '10010'
#     m = {'InstructionCode': inst_code,  # 交易号：密钥交换
#         'EntrustWay': 'I',  # 委托方式： 市场
#         'TradeSource': 'I',   # 交易发起方：市场
#         'InstNo': AgriculturalBankTradeConstData.InstNo,   # 市场编号
#         'InstSerial': ab_util.create_ab_inst_serial(ab_util.get_service_name_for_ab(inst_code)),  # 市场流水号
#     }
#     s = s.format(**m)
#
#     c_msg = ab_util.encrypt_msg(s, new_pack_key)
#
#     mac = ab_util.make_mac(c_msg)
#     header = ab_util.make_header(len(c_msg), head_msg_type='R', trade_no=inst_code, mch_id=AgriculturalBankTradeConstData.InstN, mac=mac)
#
#     package = header+c_msg
#
#     r, n = send(package)
#
#     header, cr_msg = r[:41], r[41: n]
#
#     if not ab_util.check_header(header):
#         pass # TODO
#     msg = ab_util.decrypt_msg(cr_msg)
#     mac, msg_size = ab_util.get_mac_and_msg_size_from_header()
#     if not ab_util.check_msg(msg, mac, msg_size):
#         pass # TODO
#
#     data = make_dict_from_xml(msg)
#
#     if ab_util.is_successful_result_code(data['Code']):
#         pin_key = data['PinKey']
#         mac_key = data['MacKey']
#         pag_key = data['PagKey']
#
#         # TODO save(pin_key,mac_key,pag_key)
#     else:
#         # error TODO
#         pass



# def transfer_key():
#     s = '<root><pub><InstructionCode>{InstructionCode}</InstructionCode>' \
#         '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
#         '<TradeSource>{TradeSource}</TradeSource>' \
#         '<InstNo>{InstNo}</InstNo></pub>' \
#         '<Serial><InstSerial>{InstSerial}</InstSerial></Serial>' \
#         '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business>' \
#         '</root>'
#     inst_code = '10009'
#     m = {'InstructionCode': inst_code,  # 交易号：密钥交换
#         'EntrustWay': 'I',  # 委托方式： 市场
#         'TradeSource': 'I',   # 交易发起方：市场
#         'InstNo': AgriculturalBankTradeConstData.InstNo,   # 市场编号
#         'InstSerial': ab_util.create_ab_inst_serial(ab_util.get_service_name_for_ab(inst_code)),  # 市场流水号
#     }
#     s = s.format(**m)
#
#     pack_key, _, mac_key = ab_util.get_key()
#     c_msg = ab_util.encrypt_msg(s, pack_key)
#
#
#     mac = ab_util.make_mac(c_msg, mac_key)
#     header = ab_util.make_header(len(c_msg), head_msg_type='R', trade_no=inst_code, mch_id=AgriculturalBankTradeConstData.InstN, mac=mac)
#
#     package = header+c_msg
#
#     r, n = send(package)
#
#     header, cr_msg = r[:41], r[41: n]
#
#     if not ab_util.check_header(header):
#         pass # TODO
#     msg = ab_util.decrypt_msg(cr_msg)
#     mac, msg_size = ab_util.get_mac_and_msg_size_from_header()
#     if not ab_util.check_msg(msg, mac, msg_size):
#         pass # TODO
#
#     data = make_dict_from_xml(msg)
#
#     if ab_util.is_successful_result_code(data['Code']):
#         pin_key = data['PinKey']
#         mac_key = data['MacKey']
#         pag_key = data['PagKey']
#
#         # TODO save(pin_key,mac_key,pag_key)
#     else:
#         # error TODO
#         pass





