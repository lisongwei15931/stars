# -*- coding:utf-8 -*-
import hashlib
import random
import string
import base64
import urllib
import xml
import xml.dom.minidom
import xml.sax
import xml.sax.handler
import rsa
from cffi import VerificationError

from stars.apps.customer.finance.alipay.alipay_config import AliPayConfig
from stars.apps.customer.finance.finance_exception import AliPayException
from stars.apps.customer.finance.alipay.log import ali_pay_log as logging


def getNonceStr():
    return ''.join(random.sample(string.letters+string.digits, 32))


def to_url_params(data):
    return '&'.join(['{}={}'.format(k,v) for k,v in data.items()])


def makeXml(m, with_cdata=True):
    if with_cdata:
        ls = []
        for k, v in m.iteritems():
            if v is not None and v != '':
                ls.append('<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value=v))
            else:
                '<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value='')
            # ls = ['<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value=v) for k, v in m.iteritems()]
    else:
        ls = ['<{tag}>{value}</{tag}>'.format(tag=k, value=v) for k, v in m.iteritems()]
    return '<xml>' + ''.join(ls) + '</xml>'


def makeSign(m, sign_type='md5'):
    """

    :param m: 待签名参数
    :param sign_type: 签名类型
    :return: 签名。如果类型为RSA，返回的是base64编码后经quote编码的签名
    """
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
    if not sign_type or sign_type.lower() == 'md5':
        s += AliPayConfig.MD5_KEY
        return hashlib.md5(s).hexdigest().lower(), ''
    elif sign_type.lower() == 'rsa':
        key = rsa.PrivateKey.load_pkcs1(AliPayConfig.MY_RSA_PRIVATE_KEY)
        sign_r = rsa.sign(s, key, 'SHA-1')
        # sign = base64.b64encode(sign_r)
        sign = urllib.quote(base64.b64encode(sign_r))
        return sign, s


def checkSign(data):
    temp = {k: v for k,v in data.items()}
    sign = temp.pop('sign')
    sign_type = temp.pop('sign_type')
    if not sign_type or sign_type.lower() == 'md5':
        mysign = makeSign(temp, sign_type)
        ret = 0 if sign == mysign else 1
    elif sign_type.lower() == 'rsa':
        ks = temp.keys()
        ks.sort()
        ls = []
        for k in ks:
            if temp[k] not in (None, ''):
                if isinstance(temp[k], unicode):
                    ls.append('{k}={v}'.format(k=k, v=temp[k].encode('utf8')))
                else:
                    ls.append('{k}={v}'.format(k=k, v=temp[k]))
        s = '&'.join(ls)
        try:
            sh = base64.b64decode(urllib.unquote(sign))
            public_key = rsa.PublicKey.load_pkcs1_openssl_pem(AliPayConfig.ALI_RSA_PUBLIC_KEY)
            ret = 0 if rsa.verify(s, sh, public_key) else 1
        except VerificationError as e:
            logging.exception(e)
            ret = 1
    else:
        raise ValueError()

    if ret != 0:
        logging.exception('check sign faied')
        logging.exception(data)
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


def make_dict_from_xml(content):
    xh = XMLHandler()
    try:
        xml.sax.parseString(content, xh)
        fromWxData = xh.getDict()
        if 'xml' in fromWxData:
            del fromWxData['xml']
    except Exception as e:
        logging.exception(e)
        raise AliPayException(AliPayException.ERROR_XML_FORMAT, e.message)
    return fromWxData
