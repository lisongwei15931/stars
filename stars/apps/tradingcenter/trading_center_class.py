#coding=utf-8
import random
import threading
import pusher
from django.db import transaction

p = pusher.Pusher(
  app_id='146724',
  key='e666e112da02614bfea7',
  secret='28cacf3e91d1471923f8',
  ssl=True,
  port=443
)
list = ['strike_price','net_change','bid_price','ask_price','bid_vol','ask_vol','volume']


class PushTrigger:
    @transaction.atomic  
    def pushupdate(self,msg):
        p.trigger('push_channel','pushupdate',msg)
    @transaction.atomic  
    def pushadd(self,msg):
        p.trigger('push_channel','pushadd',msg)

class RandomPusher(threading.Thread):
    def run(self):
        while True:
            id = random.randint(1, 10)
            name = random.choice(list)
            value = random.randint(1,9999)
            p.trigger('random_channel', 'randomupdate', {'message': {'id':id,'name':name,'value':value}})



class PushData:
    def pushdata(self,channel_name, event_name,msg):
        p.trigger(channel_name,event_name,{'message': msg})
        

class TestConnect:
    def pushdata(self):
        id = random.randint(1, 19)
        name = random.choice(list)
        value = random.randint(1,9999)
        p.trigger('random_channel', 'randomupdate', {'message': {'id':id,'name':name,'value':value}})
        
# ss = PushData()
# ss.pushdata('push_channel', 'pushupdate', {'id':1,'name':'Price','value':236})
