# -*- coding: utf-8 -*-s

import json
import random
import datetime

from django.conf import settings
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template import Context

from stars.apps.accounts.forms import (RegisterForm, IdentityForm, LoginForm,
                                       ForgetPwForm, ResetPwForm,
                                       local_mobile_phone_validator)
from stars.apps.accounts.models import UserProfile, Captcha
from stars.apps.commission.models import UserBalance, UserAssetDailyReport
from stars.apps.public.send_message import send_message


def check_mobile_phone(request):
    mobile_phone = request.GET.get('mobile_phone', '')
    result = {}
    if not local_mobile_phone_validator(mobile_phone):
        result['error'] = u'无效的手机号码。'
        return HttpResponse(json.dumps(result), content_type='application/json', status=200)
    try:
        UserProfile.objects.get(mobile_phone=mobile_phone)
        result['error'] = u'此号码已经被注册。'
    except UserProfile.DoesNotExist:
        result['error'] = u''
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)

def check_register_mobile_phone(request):
    if request.is_ajax():
        mobile_phone = request.GET.get('mobile_phone', '')
        result = {}
        if not local_mobile_phone_validator(mobile_phone):
            if not mobile_phone:
                result['error']=u'手机号码不能为空！'
                return HttpResponse(json.dumps(result), content_type='application/json', status=200)
            result['error'] = u'无效的手机号码。'
            return HttpResponse(json.dumps(result), content_type='application/json', status=200)
        try:
            UserProfile.objects.get(mobile_phone=mobile_phone)
        except UserProfile.DoesNotExist:
            result['error'] = u'不是注册过的手机号码'
        return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def check_username(request):
    username = request.GET.get('username', '')
    result = {}
    if username:
        try:
            user = User.objects.get(username=username)
            result['error'] = (u'用户名被占用。')
        except User.DoesNotExist:
            result['error'] = u''
        return HttpResponse(json.dumps(result), content_type='application/json', status=200)
    else:
        result['error'] = u''
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def check_introducer(request):
    introducer = request.GET.get('introducer', '')
    result = {}
    if introducer:
        try:
            user = User.objects.get(username=introducer)
            result['error'] = u''
        except User.DoesNotExist:
            result['error'] = u'没有这个用户，请重新输入'
        return HttpResponse(json.dumps(result), content_type='application/json', status=200)
    else:
        result['error'] = u''
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def register(request):
    if request.method == 'POST':
        post = True
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            mobile_phone = request.POST.get('mobile_phone', '')
            email = request.POST.get('email', '')
            introducer = request.POST.get('introducer', '')
            new_user = User.objects.create(username=username, password=make_password(password),
                                           email=email)
            user_balance = UserBalance.objects.create(user=new_user)
            today = datetime.datetime.now().date()
            user_asset_daily_report = UserAssetDailyReport.objects.create(user=new_user,
                                        target_date=today)
            # login
            user = authenticate(username=username, password=password)
            login(request, user)
            try:
                current_userprofile = new_user.userprofile
                current_userprofile.mobile_phone = mobile_phone
                current_userprofile.introducer = introducer
            except UserProfile.DoesNotExist:
                current_userprofile = UserProfile.objects.create(user=new_user, mobile_phone=mobile_phone)
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                current_ip =  request.META['HTTP_X_FORWARDED_FOR']
            else:
                current_ip = request.META['REMOTE_ADDR']
            current_userprofile.register_ip = current_ip
            current_userprofile.save()
            return redirect('accounts:set_identity', current_userprofile.id)
    else:
        post = False
        form = RegisterForm()
    context = {'form': form,
               'post': post}
    return render(request, 'accounts/register.html', context)


def set_identity(request, userprofile_id):
    try:
        current_userprofile = UserProfile.objects.get(id=int(userprofile_id))
        current_user_id = current_userprofile.user.id
    except:
        return HttpResponse(u'不存在此用户')
    if request.method == 'POST':
        post = True
        form = IdentityForm(request.POST, request.FILES, instance=current_userprofile)
        if form.is_valid():
            form.save()
            return redirect('accounts:set_identity', 1)
    else:
        post = False
        form = IdentityForm(instance=current_userprofile)
    context = {'form': form,
               'current_user_id': current_user_id,
               'post': post}
    return render(request, 'accounts/set_identity.html', context)


def register_finish(request, user_id):
    try:
        current_user = User.objects.get(id=int(user_id))
    except:
        return HttpResponse(u'不存在此用户')
    context = {'current_user': current_user}
    return render(request, 'accounts/register_finish.html', context)


def user_login(request):

    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        next_url = request.session.get('login_from', '/')

        if user:
            login(request, user)
            return redirect(next_url )
        else:
            error = u'用户名/密码错误'
    else:
        form = LoginForm()
        next_url = request.GET.get('next', '/')
        request.session['login_from'] = next_url

    context = {'form': form, 'error': error}

    return render(request, 'accounts/login.html', context)


def send_captcha(request):
    phone = request.GET.get('phone', '')
    if phone:
        recipient = phone
    else:
        result = {'result': False, 'msg': '请输入手机号'}
        return HttpResponse(json.dumps(result), content_type='application/json', status=200)
    new_captcha = random.randint(100000, 999999)
    current_captcha = Captcha.objects.get_or_create(recipient=recipient)[0]
    current_captcha.captcha = new_captcha
    current_captcha.save()
    send_content = u'您的验证码是：%s。请不要把验证码泄露给其他人。' % str(new_captcha)
    if phone:
        (response_code, response_msg) = send_message(recipient, send_content)
        if response_code == '2':
            result = {'result': True, 'msg': response_msg}
        else:
            result = {'result': False, 'msg': response_msg}
        result = {'result': True, 'msg': '验证码已发送'}

    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def user_agreement(request):
    context = {}
    return render(request, 'accounts/user_agreement.html', context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def forgetpw(request):
    form = ForgetPwForm()
    post = False

    if request.method == 'POST':
        form = ForgetPwForm(request.POST)
        post = True

        if form.is_valid():
            mobile_phone = form.clean_mobile_phone()
            captcha = form.clean_captcha()

            try :
                captacha_db = Captcha.objects.get(recipient = mobile_phone).captcha

                if captacha_db != captcha :
                    return redirect('accounts:forgetpw')

                userprofile = UserProfile.objects.get(mobile_phone=mobile_phone)
                userid = userprofile.user.id
                request.session['userid'] = userid
                return redirect('accounts:resetpw')

            except Captcha.DoesNotExist ,UserProfile.DoesNotExist:
                return redirect('accounts:forgetpw')
        else:
            context = {'form':form,'post':post}
            return render(request,'accounts/forgetpw.html',context)
    context = {'form':form,'post':post}
    return render(request,'accounts/forgetpw.html',context)


def resetpw(request):
    form = ResetPwForm()
    post = False
    userid = request.session.get('userid',None)

    try :
        user = User.objects.get(pk=userid)
    except User.DoesNotExist :
        return redirect('accounts:forgetpw')



    if request.method =='POST' :
        form = ResetPwForm(request.POST)
        post = True

        if form.is_valid():
            password = form.cleaned_data['password']
            re_password = form.clean_re_password()

            if password == re_password :
                password = make_password(password)
                user.password = password
                user.save()

                return redirect('accounts:resetpw_finish')
    context = {'form':form ,'post':post ,'user':user}
    return render(request,'accounts/resetpw.html',context)

def resetpw_finish(request):
    userid = request.session.get('userid',None)

    try :
        user = User.objects.get(pk=userid)
    except User.DoesNotExist :
        return redirect('accounts:forgetpw')

    context = {'user':user}
    try :
        del request.session['userid']
    except KeyError:
        pass

    return  render(request,'accounts/resetpw_finish.html',context)

