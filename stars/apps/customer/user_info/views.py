# -*- coding: utf-8 -*-
from __future__ import division

from django.shortcuts import render

from rest_framework.views import APIView

from stars.apps.address.models import Province, District, City
from stars.apps.customer.safety.utils import mask_mobile, mask_mail_url
from stars.apps.customer.user_info.serializers import UserInfoSerializer


class UserInfoView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        tpl = 'customer/user_info/user_info.html'
        data = UserInfoSerializer(user.userprofile).data
        self.set_user_readonly_info(data, user)

        regions = self.get_regions(user)

        m = {
            'user_info': data,
             'frame_id': 'user_info',
            'region': regions,
             }
        return render(request, tpl, m)

    def get_regions(self, user):
        regions = {'provinces': list(Province.objects.all()),
                   }
        if user.userprofile.region:
            regions['cities'] = City.objects.filter(province_id=user.userprofile.region.city.province_id)
            regions['districts'] = District.objects.filter(city_id=user.userprofile.region.city_id)
        return regions

    def set_user_readonly_info(self, data, user):
        if not data.get('real_name'):
            data['real_name'] = user.userprofile.real_name if user.userprofile.real_name is not None else ''
        if not data.get('mobile_phone'):
            data['mobile_phone'] = mask_mobile(user.userprofile.mobile_phone)
        if not data.get('email'):
            data['email'] = mask_mail_url(user.email)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        data['sex'] = {'male': 2, 'female': 3, 'hid': 1}.get(data.get('sex'), 1)
        data['interest'] = data.get('interest', '').strip()
        # data['birthday'] = None
        if 'address' not in data:
            data['address'] = ''

        ctx = {'frame_id': 'user_info',
               }

        if (data.get('province_id') or data.get('city_id')) and not data.get('district_id'):
            tpl = 'customer/user_info/user_info.html'
            self.set_error_ret_data(ctx, data, user)
            return render(request, tpl, ctx)

        data['user'] = user

        ser = UserInfoSerializer(data=data)

        if ser.is_valid() :#and \
            user.userprofile.sex = data['sex']
            user.userprofile.birthday = data['birthday'] if data['birthday'] else None
            user.userprofile.address = data['address']
            user.userprofile.interest = data['interest']
            user.userprofile.nickname = data['nickname']
            if data.get('district_id'):
                data['region'] = District.objects.get(pk=data['district_id'])
                user.userprofile.region = data['region']

            user.userprofile.save(update_fields=['sex', 'birthday', 'address', 'interest', 'nickname',
                                                 'region',
                                                 'modified_date',
                                                 'modified_time',
                                                 ])

            tpl = 'customer/user_info/user_info_update_suc.html'
            return render(request, tpl, ctx)
        else:

            tpl = 'customer/user_info/user_info.html'

            self.set_error_ret_data(ctx, data, user)
            return render(request, tpl, ctx)

    def set_error_ret_data(self, ctx, data, user):
        if data.get('province_id'):
            data['province_id'] = int(data['province_id'])
        if data.get('city_id'):
            data['city_id'] = int(data['city_id'])
        self.set_user_readonly_info(data, user)
        ctx['region'] = self.get_regions(user)
        ctx['user_info'] = data
        ctx['region_err_msg'] = u'请您填写完整的地区信息'

