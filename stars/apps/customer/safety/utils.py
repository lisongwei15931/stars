# -*- coding: utf-8 -*-
import random
import string

from django.core import mail
from django.conf import settings
from django.template import loader, Context
from django.contrib.sites.models import Site
import re


def mask_mail_url(mail_url):
    if mail_url:
        return '{}***{}'.format(mail_url[0], mail_url[mail_url.find('@')-1:])
    return ''


def mask_mobile(mobile):
    if mobile:
        return '{}***{}'.format(mobile[:3] , mobile[-3:])
    return ''


def check_pwd(pwd):
    if not pwd:
        return False, u'密码不能为空'
    elif len(str(pwd)) < 6 or len(str(pwd)) > 20:
        return False, u'密码位数必须为6-20'
    else:
        return True, ''


def is_valid_mail_addr(addr):
    p=re.compile('[_a-z\d\-\./]+@[_a-z\d\-]+(\.[_a-z\d\-]+)*(\.(info|biz|com|edu|gov|net|am|bz|cn|cx|hk|jp|tw|vc|vn))$')
    return p.match(addr) is not None


def is_valid_id_card_num(id):
    p=re.compile('^(\d{15}$|^\d{18}$|^\d{17}(\d|X|x))$')
    return p.match(id) is not None


def send_update_mail_confirmation(to, link):
    """
    发送确认邮件
    """
    ctx = Context({
        'period_validity': u'24小时',
        'link': link,
        'site': Site.objects.get_current(),
    })
    subject_tpl = loader.get_template('customer/safety/email/'
                                      'confirmation_subject.txt')
    body_tpl = loader.get_template('customer/safety/email/'
                                   'confirmation_body.txt')

    mail.send_mail(
        subject_tpl.render(ctx).strip(),
        body_tpl.render(ctx),
        settings.OSCAR_FROM_EMAIL,
        (to,)
    )


def send_updated_mail_notification(to, new_mail, update_time):
    """
    发送确认邮件
    """
    ctx = Context({
        'old_email': to,
        'new_email': mask_mail_url(new_mail),
        'update_time': update_time,
        'period_validity': u'24小时',
    })
    subject_tpl = loader.get_template('customer/safety/email/'
                                      'updated_mail_notification_subject.txt')
    body_tpl = loader.get_template('customer/safety/email/'
                                   'updated_mail_notification_body.txt')

    mail.send_mail(
        subject_tpl.render(ctx).strip(),
        body_tpl.render(ctx),
        settings.OSCAR_FROM_EMAIL,
        (to,)
    )


def generate_sms_verification_code(len=4):
    return ''.join(random.sample(string.digits, len if len >=4 else 4))


def get_choice_value_list(c):
    return [v[0] for v in c]


def convert_none_or_empty_to_0(value):
    return value if value else 0
