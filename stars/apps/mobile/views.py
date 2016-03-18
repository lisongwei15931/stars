#coding=utf-8

from django.shortcuts import render

def home(request):
    device = request.GET.get('device','1')
    context = {'device':device}
    template = 'mobile/index.html'
    return render(request,template,context)


def home_test(request):
    #: 手机测试页面

    device = request.GET.get('device', '1')
    context = {'device': device}
    template = 'mobile/index_test.html'
    return render(request, template, context)
