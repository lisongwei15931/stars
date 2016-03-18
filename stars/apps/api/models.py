# -*- coding: utf-8 -*-s


from django.db import models


OPERAING_SYSTEM_CHOICE = (('1', 'IOS'), ('2', 'Android'))

class App(models.Model):
    version = models.CharField(max_length=64, verbose_name=u'版本号')
    operaing_system = models.CharField(max_length=16,
                                       choices=OPERAING_SYSTEM_CHOICE,
                                       default='1',
                                       verbose_name=u'操作系统')
    description = models.TextField(blank=True, verbose_name=u'版本描述')
    app_file = models.FileField(upload_to="apps", verbose_name=u'APP文件')
    need_forced_update = models.BooleanField(default=False,
                                             verbose_name=u'是否需要强制更新')

    class Meta:
        verbose_name = verbose_name_plural = u'移动APP'
        unique_together = ('version', 'operaing_system')

    def __unicode__(self):
        return '_'.join([self.get_operaing_system_display(), self.version])
