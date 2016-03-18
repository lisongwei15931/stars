# -*- coding: utf-8 -*-s


import requests
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from django.conf import settings


message_account = settings.MESSAGE_ACCOUNT
message_password = settings.MESSAGE_PASSWORD
message_url = settings.MESSAGE_URL


def send_message(phone_number, content):
    params = {'account': message_account,
              'password': message_password,
              'mobile': phone_number,
              'content': content}
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    res = requests.post(message_url, data=params, headers=headers)
    xml_text = ET.fromstring(res.content)
    code = ''
    msg = ''
    for elem in xml_text:
        if 'code' in elem.tag:
            code = elem.text
        if 'msg' in elem.tag:
            msg = elem.text

    return (code, msg)
