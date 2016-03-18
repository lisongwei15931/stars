# -*- coding:utf-8 -*-
import hashlib
import logging
import random
import string
import xml
import xml.dom.minidom
import xml.sax
import xml.sax.handler

from stars.apps.customer.finance.finance_exception import WxException
from stars.apps.customer.finance.weixin.common_const import WxNativePaymentConstData


def getNonceStr():
    return ''.join(random.sample(string.letters+string.digits, 32))

def to_url_params(data):
    return '&'.join(['{}={}'.format(k,v) for k,v in data.items()])

def makeXml(m, with_cdata=True):
    if with_cdata:
        ls = []
        for k, v in m.iteritems():
            if v is not None and v != '':
                ls.append(u'<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value=v))
            else:
                u'<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value='')
            # ls = ['<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value=v) for k, v in m.iteritems()]
    else:
        ls = [u'<{tag}>{value}</{tag}>'.format(tag=k, value=v) for k, v in m.iteritems()]
    return '<xml>' + ''.join(ls) + '</xml>'


def makeSign(m,api_key=WxNativePaymentConstData.API_KEY):
    ks = m.keys()
    ks.sort()
    ls = []
    for k in ks:
        if m[k] not in (None, ''):
            if isinstance(m[k], unicode):
                ls.append('{k}={v}'.format(k=k, v=m[k].encode('utf8')))
            else:
                ls.append('{k}={v}'.format(k=k, v=m[k]))

    # ls = ['{k}={v}'.format(k=k, v=m[k]) for k in ks if m[k] not in (None, '')]
    s = '&'.join(ls)
    # api_key = api_key
    stringSignTemp="{s}&key={api_key}".format(s=s, api_key=api_key)
    return hashlib.md5(stringSignTemp).hexdigest().upper()


def checkSign(data):
    sign = data.pop('sign')
    mysign = makeSign(data)
    data['sign'] = sign
    ret = 0 if sign == mysign else 1
    if ret != 0:
        logging.exception('mysign:' + mysign)
        logging.exception('the other sign:' + sign)
    return ret


class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attributes):
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        self.mapping[name] = self.buffer

    def getDict(self):
        return self.mapping


# def make_dict_from_xml(content):
#     content = content.decode('utf-8')
#     xh = XMLHandler()
#     xml.sax.parseString(content, xh)
#     fromWxData = xh.getDict()
#     if 'xml' in fromWxData:
#         del fromWxData['xml']
#     return fromWxData

def make_dict_from_xml(content):
    text = content.decode('utf-8')
    xh = XMLHandler()
    try:
        xml.sax.parseString(content, xh)
        fromWxData = xh.getDict()
        if 'xml' in fromWxData:
            del fromWxData['xml']
    except Exception as e:
        logging.exception(e)
        raise WxException(WxException.ERROR_XML_FORMAT, e.message)
    return fromWxData
