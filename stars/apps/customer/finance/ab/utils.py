# -*- coding: utf-8 -*-
from __future__ import division
import xml
import xml.dom.minidom
import xml.sax
import xml.sax.handler


def is_none_or_empty_or_blank(d):
    return d is None or d == '' or d.strip() == ''

def is_none_or_empty(d):
    return d is None or d == ''

class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attributes):
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        if not name.endswith('root'):
            self.mapping[name] = self.buffer if isinstance(self.buffer, unicode) else self.buffer.decode('utf8')

    def getDict(self):
        return self.mapping


def makeXml(m, with_cdata=True):
    if with_cdata:
        ls = ['<{tag}><![CDATA[{value}]]></{tag}>'.format(tag=k, value=v) for k, v in m.iteritems()]
    else:
        ls = ['<{tag}>{value}</{tag}>'.format(tag=k, value=v) for k, v in m.iteritems()]
    return '<root>' + ''.join(ls) + '</root>'


def make_dict_from_xml(content):
    content = content.decode('gbk').encode('utf8')
    content = content.rstrip('\0')
    xh = XMLHandler()
    xml.sax.parseString(content, xh)
    return xh.getDict()




