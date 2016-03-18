# -*- coding: utf-8 -*-s

from django.db import models
from ckeditor.fields import RichTextField

CATEGORY_CHOICE = (
    (1, u'静态页面'),
    (2, u'公告'),
    (3, u'新品上市'),
    (4, u'购物须知'),
    (5, u'其他'),
)

class FlatPageNew(models.Model):
    title = models.CharField(default='', db_index=True, max_length=200, verbose_name=u'标题')
    category = models.IntegerField(default=1, db_index=True, verbose_name=u'类别', choices=CATEGORY_CHOICE)
    url = models.CharField(default='', max_length=200, verbose_name=u'URL')
    content = RichTextField(u'正文')
    enable = models.BooleanField(default=False, db_index=True, verbose_name=u'是否启用')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
