# coding=utf-8
import logging

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.response import Response

from stars.apps.accounts.models import UserProfile
from stars.apps.api.common.views import CommonPermissionAPIView
from stars.apps.api.error_result import err_result, SUCCESS_CODE, SYSTEM_ERR_CODE


class UserBaseInfoView(CommonPermissionAPIView):

    def get(self, request, format=None):
        """
        获取用户基本信息
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        user = request.user
        try:
            user1 = user.userprofile
            data = {'username': user.username,
                    'username_editable': not user1.username_checked,
                    'mobile': user1.mobile_phone,
                    'nickname': user1.nickname,
                    'email': user.email,
                    'avatar': user1.avatar.url if user1.avatar else '',
                    'sex': user1.sex,
                    'birthday': user1.birthday if user1.birthday else '',
                    }

            m = err_result(SUCCESS_CODE, u'获取用户信息成功').msg
            m['data'] = data
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取用户信息失败').msg)

    def post(self, request, format=None):
            """
            修改用户基本信息
            :param request:
            :param format:
            :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
            """

            data = request.data
            user = request.user
            user1 = user.userprofile

            chang_username = False

            try:
                user_change_fields = []
                if 'username' in data and data['username'] != user.username:
                    if data['username'] in [None, '']:
                        return Response(err_result(258, u'用户名无效').msg)
                    elif user1.username_checked:
                        return Response(err_result(257, u'用户名已经修改过，不可再次修改').msg)
                    elif User.objects.filter(username=data['username']).exclude(pk=user.pk).exists() \
                            or UserProfile.objects.filter(mobile_phone=data['username']).exclude(pk=user1.pk):
                        return Response(err_result(256, u'该用户名已经被注册').msg)
                    else:
                        user.username = data['username']
                        user1.username_checked = True
                        chang_username = True
                        user_change_fields.append('username')
                if 'email' in data:
                    user.email = data.get('email', '')
                    user_change_fields.append('email')

                profiles_change_fields = set(data.keys()) & {'sex', 'birthday', 'nickname'}

                with transaction.atomic():
                    if user_change_fields:
                        user.save()

                    if profiles_change_fields or chang_username == True:
                        for ele in profiles_change_fields:
                            if hasattr(user1, ele):
                                setattr(user1, ele, data[ele])
                        user1.save()

                m = err_result(SUCCESS_CODE, u'修改用户信息成功').msg
                return Response(m)
            except Exception as e:
                logging.exception(e)
                return Response(err_result(SYSTEM_ERR_CODE, u'修改用户信息失败').msg)
