#coding=utf-8

from oscar.core.loading import get_class,get_model
import datetime

SystemConfig = get_model('commission', 'SystemConfig')


def open_close_date():
    '''
    #页面显示开市闭市时间
    '''
    open_close_msg =""
    open_or_close = False
    system_config = SystemConfig.objects.first()
    now = datetime.datetime.now().time()
    open_time = system_config.bank_start_time.strftime('%H:%M')
    close_time = system_config.bank_end_time.strftime('%H:%M')
    if system_config.bank_start_time < now and now < system_config.bank_end_time:
        open_close_msg = u"开市(当日%s-%s)"%(open_time,close_time)
        open_or_close = True
    else:
        open_close_msg = u"闭市(%s-次日%s)"%(close_time,open_time)
        open_or_close = False
        
    return open_or_close,open_close_msg
    