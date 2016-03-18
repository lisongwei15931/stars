# -*- coding: utf-8 -*-s
from __future__ import absolute_import
import pusher
import datetime
import urllib, urllib2
import json
from stars.celery import app


#p = pusher.Pusher(
#  app_id='146724',
#  key='e666e112da02614bfea7',
#  secret='28cacf3e91d1471923f8',
#  ssl=True,
#  port=443
#)
#list = ['strike_price','net_change','bid_price','ask_price','bid_vol','ask_vol','volume']


class PushTriggerTest:
    @app.task()
    def pushupdate(self,msg):
        get_post_response({"task":"update", "data":msg})
        #p.trigger('push_channel','pushupdate',msg)
    @app.task()
    def pushadd(self,msg):
        get_post_response({"task":"add", "data":msg})
        #p.trigger('push_channel','pushadd',msg)
    @app.task()
    def pushmoney(self,msg):
        get_post_response({"task":"changemoney", "data":msg})

def get_post_response(post_body):
    url = "http://139.129.98.159:3001/broadcast/"
    params = {'msg': json.dumps(post_body)}
    post_data = urllib.urlencode(params);
    req = urllib2.Request(url, post_data);
    req.add_header('User-Agent', "firefox");
    req.add_header('Content-Type', 'application/x-www-form-urlencoded');
    req.add_header('Cache-Control', 'no-cache');
    req.add_header('Accept', '*/*');
    req.add_header('Connection', 'Keep-Alive');
    resp = urllib2.urlopen(req);
    
    ret = resp.read()

    return ret

