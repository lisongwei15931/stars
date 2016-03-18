# -*- coding: utf-8 -*-
import json
import random
import string
import xml
from datetime import *

import httplib2

from stars.apps.customer.finance.alipay.alipay_config import AliPayConfig
from stars.apps.customer.finance.alipay.utils import XMLHandler, makeSign, makeXml, make_dict_from_xml, checkSign
from stars.apps.customer.finance.finance_exception import AliPayException


class QueryOrderXMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.mapping = {}
        self.log_list = []
        self.is_in_log_list = False

    def startElement(self, name, attributes):
        self.buffer = ""
        if name == 'AccountQueryAccountLogVO':
            self.log_list.append({})
            self.is_in_log_list = True

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):

        if name == 'AccountQueryAccountLogVO':
            self.is_in_log_list = False
        elif self.is_in_log_list == True:
            self.log_list[-1][name]=self.buffer
        else:
            self.mapping[name] = self.buffer

    def getDict(self):
        if self.log_list:
            self.mapping['bills'] = self.log_list
        return self.mapping


class AliPayApi(object):
    __ALI_PAY_URL = '{gateway}&_input_charset={charset}'.format(gateway=AliPayConfig.ALI_PAY_GATEWAY_NEW,
                                                                       charset=AliPayConfig.INPUT_CHARSET,
                                                                       )

    @staticmethod
    def generate_out_trade_no(user_id):
        """
        生成订单号
        :param user_id: 用户id
        :return: 订单号
        """
        s = 'al'+'{:0<18}'.format(datetime.now().strftime('%Y%m%d%H%M%S%f')[2:20])+''.join(random.sample(string.letters, 3))+'{:0>9}'.format(user_id)[:9]
        assert(len(s) == 32)
        return s

    @staticmethod
    def make_dict_from_resp(resp, content, xml_handler=XMLHandler):
        content_type = resp.get('content-type', '')
        if not content_type:
            content_type = resp.get('content_type', '')

        content.decode('utf8')
        if 'xml' in content_type:
            if not xml_handler:
                xh = XMLHandler()
            else:
                xh = xml_handler()
            xml.sax.parseString(content, xh)
            fromWxData = xh.getDict()
        elif 'json' in content_type:
            fromWxData = json.loads(content)
        else:
            raise ValueError(u'content-type错误：不是xml也不是json')

        return fromWxData

    @staticmethod
    def query_timestamp(time_out=3):
        """
        用于防钓鱼，调用接口query_timestamp来获取时间戳的处理函数
        :param time_out: 接口超时时间
        :return: 时间戳字符串
        """

        url = AliPayConfig.ALI_PAY_GATEWAY_NEW + "service=query_timestamp&partner=" + AliPayConfig.PID + "&_input_charset=" + AliPayConfig.INPUT_CHARSET

        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "GET", body='', headers={'content-type': 'text/json'})

        result = AliPayApi.make_dict_from_resp(resp, content)

        encrypt_key = result.get('encrypt_key', '')
        return encrypt_key

    @staticmethod
    def verify_notification(notify_id, time_out=3):
        """
        对支付宝通知回来的参数notify_id合法性验证
        :param notify_id: 支付宝通知返回的参数notify_id
        :param time_out: 接口超时时间
        :return: 成功时：True; 不成功时：False
        """

        url = '{gateway}service=notify_verify&partner={pid}&' \
              'notify_id={notify_id}&_input_charset={charset}'.format(gateway=AliPayConfig.ALI_PAY_GATEWAY_NEW,
                                                                       pid=AliPayConfig.PID,
                                                                       charset=AliPayConfig.INPUT_CHARSET,
                                                                       notify_id=notify_id)

        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "GET", body='', headers={'content-type': 'text/json'})

        return content == b'true'

    @staticmethod
    def query_single_trade(trade_no=None, transaction_id=None, sign_type='MD5', time_out=6):
        """
        单笔订单交易查询。已经拿到支付宝交易号时请使用支付宝交易号查 询，如未拿到则使用订单号查询
        :param trade_no: 订单号
        :param transaction_id: 支付宝交易号
        :param time_out:
        :return:
        """
        # 检测必填参数
        data = {
            'partner': AliPayConfig.PID,
            '_input_charset': AliPayConfig.INPUT_CHARSET,
            'service': 'single_trade_query',
        }
        if transaction_id:
            data['trade_no'] = transaction_id
        elif trade_no:
            data['out_trade_no'] = trade_no
        else:
            raise ValueError(u'trade_no、ali_trade_no必须有一个')

        data['sign'] = makeSign(data, sign_type)   # 签名
        data['sign_type'] = sign_type
        req_body = '&'.join('{}={}'.format(k,v) for k,v in data.items())

        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(AliPayApi.__ALI_PAY_URL, "POST", body=req_body,
                                  headers={'content-type': 'application/x-www-form-urlencoded'})

        result = AliPayApi.make_dict_from_resp(resp, content)

        if not checkSign(result):
            raise AliPayException(AliPayException.ERROR_SIGN, u'query_single_trade返回值签名错误')

        return result


    @staticmethod
    def query_trade(gmt_start_time=None, gmt_end_time=None, page_size=5000, time_out=6, **kwargs):
        """
        账目明细分页查询
        :param gmt_start_time: 账务查询开始时间,格式为 yyyy-MM-dd HH:mm:ss.
            开始时间不能大于当前时间 和查询结束时间，并且与账 务查询结束时间的间隔不能 大于 1 天。 开始时间最早为当前时间前 3 年。
            当查询条件含有账务流水号、支付宝交易号、商户订单号、充值网银流水号中任意一个时，本参数可空，否则不可空。
            查询结果数据包含该时间点数据。
        :param gmt_end_time: 账务查询结束时间,格式为 yyyy-MM-dd HH:mm:ss.
            当查询条件含有账务流水 号、支付宝交易号、商户订 单号、充值网银流水号中任 意一个时，本参数可空，否则不可空。
            查询结果数据不包含该时间点数据。
        :prarm trans_code: 交易类型代码。多个交易类型代码之间以半角逗号“,”分隔。
                            3011 转账（含红包、集分宝等）
                            3012 收费
                            4003 充值
                            5004 提现
                            5103 退票
                            6001 在线支付
        :param page_size:每页记录数。 小于等于5000的正整数.
        :param time_out:
        :param kwargs: logon_id:交易收款账户.查询的收款账户，需要联系 支付宝绑定与商户 PID 的对 应关系。 若为空，表示查 PID 所属交易.
                        iw_account_log_id:账务流水号.
                        transaction_id:业务流水号.业务流水号字段对于交易数 据为交易号，对于转账、充值、提现等资金操作，此处为业务流水号。
                        merchant_out_order_no:商户订单号 .
                        deposit_bank_no:充值网银流水号.
                        查询优先级如下：账务流水号>业务流水号>商户订单号>充值网银流水号。当存在优先级高的参数时，优先级 低的参数无效。

        :return:
        """

        #正常返回的情况下，需要签名的参数是节点account_log_list、has_next_page、 page_no、page_size。
        # 参数 has_next_page、page_no、page_size 的值分 别是各个节点的值，参数 account_log_list 的值则是包含节点本身在内所有数据
        # accountLogList节点XML片段解析时需要expand empty element，如<memo/> 展开为<memo></memo>。
        # <response>
        #     <account_page_query_result>
        #         <account_log_list>
        #             <AccountQueryAccountLogVO>…..</AccountQueryAccountLogVO>
        #         </account_log_list>
        #         <has_next_page>F</has_next_page>
        #         <page_no>1</page_no>
        #         <page_size>5000</page_size>
        #     </account_page_query_result>
        # </response>
        # account_log_list :<account_log_list><Account QueryAccountLogVO>...</A ccountQueryAccountLogVO ></account_log_list>
        # has_next_page: F
        # page_no: 1
        # page_size: 5000

        data = {
            'partner': AliPayConfig.PID,
            '_input_charset': AliPayConfig.INPUT_CHARSET,
            'service': 'account.page.query',
        }
        k = {'logon_id', 'iw_account_log_id', 'transaction_id', 'merchant_out_order_no', 'deposit_bank_no',}
        if not k.intersection(kwargs.keys()) and (not gmt_end_time or not gmt_start_time):
            raise ValueError(u'缺少必要的查询参数')

        for ele in k.intersection(kwargs.keys()):
            if ele == 'transaction_id':
                data['trade_no'] = kwargs[ele]
            else:
                data[ele] = kwargs[ele]

        if gmt_start_time and gmt_end_time:
            data['gmt_start_time'] = gmt_start_time
            data['gmt_end_time'] = gmt_end_time

        page_no = 1
        while True:
            data['page_no'] = page_no
            data['sign'] = makeSign(data)   # 签名
            data['sign_type'] = AliPayConfig.SIGN_TYPE
            req_body = '&'.join('{}={}'.format(k,v) for k,v in data.items())

            h = httplib2.Http(".cache", timeout=time_out)
            resp, content = h.request(AliPayApi.__ALI_PAY_URL, "POST", body=req_body,
                                      headers={'content-type': 'application/x-www-form-urlencoded'})

            # 验证签名
            sign_m = {}
            start = content.find('<account_log_list>')
            end = content.find('</account_log_list>')
            if start!= -1 and end != -1:
                end += len('</account_log_list>')
                sign_m['account_log_list'] = content[start: end]

            result = AliPayApi.make_dict_from_resp(resp, content, xml_handler=QueryOrderXMLHandler)
            for ele in ['has_next_page', 'page_no', 'page_size', 'sign', 'sign_type']:
                sign_m[ele] = result.get(ele, '')

            if not checkSign(sign_m):
                raise AliPayException(AliPayException.ERROR_SIGN, u'query_single_trade返回值签名错误')

            yield result.get('bills', [])

            if result['has_next_page'] != 'T':
                break

            page_no = int(result['page_no'])
