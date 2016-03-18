# coding=utf-8
import logging
from collections import namedtuple

from django.db import transaction, connection
from rest_framework.response import Response

from stars.apps.address.models import ReceivingAddress, District, Province
from stars.apps.api.common.views import CommonPermissionAPIView, AllowAnyUserAPIView
from stars.apps.api.error_result import err_result, SUCCESS_CODE, SYSTEM_ERR_CODE, ERROR_PARAM, DOES_NOT_EXIST_CODE
from stars.apps.api.serializers import ReceivingAddressSerializer, UserPickupAddressSerializer
from stars.apps.commission.models import UserPickupAddr


class AddressAllView(AllowAnyUserAPIView):

    def get(self, request, format=None):
        """
        获取收货地址列表
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        try:
            qs = Province.objects.filter().order_by('name')
            data = []
            for r in qs:
                cities = []
                data.append({'province': {'id': r.pk, 'name': r.name, 'city': cities}})
                for c in r.city_set.all():
                    districts = []
                    cities.append({'id': c.pk, 'name': c.name, 'districts': districts})
                    for d in c.district_set.all():
                        districts.append({'id': d.id, 'name': d.name})

            m = err_result(SUCCESS_CODE, u'获取收货地址成功').msg
            m['data'] = data
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取收货地址失败').msg)


class RegionListView(AllowAnyUserAPIView):

    def get(self, request, format=None):
        """
        获取地区列表
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        try:
            sql = 'select p.id ,p.name, c.id,c.name, d.id,d.name ' \
                  'from address_province as p inner join address_city as c on (p.id = c.province_id)' \
                  ' inner join address_district as d on (c.id=d.city_id)' \
                  ' order by convert(p.name using gbk),convert(c.name using gbk), convert(d.name using gbk)'
            c = connection.cursor()

            c.execute(sql)
            Row = namedtuple('Row', 'p_id p_name c_id c_name d_id d_name')
            rs = []

            r = c.fetchone()
            d = Row(*r)
            rs.append({'id': d.p_id,
                       'name': d.p_name,
                       'cities': [{'id': d.c_id,
                                   'name': d.c_name,
                                   'districts': [{'id': d.d_id,
                                                  'name': d.d_name}]
                                   }]
                       })
            for r in c.fetchall():
                d = Row(*r)
                last_p = rs[-1]
                if d.p_id != last_p['id']:
                    rs.append({'id': d.p_id,
                               'name': d.p_name,
                               'cities': [{'id': d.c_id,
                                           'name': d.c_name,
                                           'districts': [{'id': d.d_id,
                                                  'name': d.d_name}]
                                           }]
                               })
                elif d.c_id != last_p['cities'][-1]['id']:
                    last_p['cities'].append({'id': d.c_id,
                                           'name': d.c_name,
                                           'districts': [{'id': d.d_id,
                                                  'name': d.d_name}]
                                           })
                else:
                    last_p['cities'][-1]['districts'].append({'id': d.d_id,
                                                              'name': d.d_name})

            m = err_result(SUCCESS_CODE, u'获取地区成功').msg
            m['data'] = rs
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取地区失败').msg)


class AddressListView(CommonPermissionAPIView):

    def get(self, request, format=None):
        """
        获取用户自己的收货地址列表
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        try:
            user = request.user
            q = ReceivingAddress.objects.filter(user=user)
            rs = ReceivingAddressSerializer(q, many=True).data

            m = err_result(SUCCESS_CODE, u'获取收货地址成功').msg
            m['data'] = rs
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取收货地址失败').msg)


class AddressView(CommonPermissionAPIView):

    __update_items = {'is_default': None,
                              'mobile': 'mobile_phone',
                              'address': None,
                              'district_id': None,
                              'name': 'consignee',
                                'telephone': None,
                                'email': None,
                                }

    def post(self, request, address_id=None, format=None):
        """
        用户新增或修改提货地址
        :param request:
        :param address_id：收货地址id
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        data = request.data
        event_text = u'添加' if address_id is None else u'修改'
        user = request.user

        need_refresh_default_flag = False
        try:
            if address_id is None:
                address = ReceivingAddress(user=user)
                must_items = {
                    # 'is_default': None,
                              'mobile': 'mobile_phone',
                              'address': None,
                              'district_id': None,
                              'name': 'consignee'}
                if not set(must_items.keys()).issubset(set(data.keys())):
                    raise KeyError

            else:
                address = ReceivingAddress.objects.get(pk=address_id, user_id=user.id)

                if address.is_default is False and bool(data.get('is_default', False)) is True:
                    need_refresh_default_flag = True

            for k, v in self.__update_items.items():
                if k in data:
                    name = v if v is not None else k
                    setattr(address, name, data[k])

            if data.get('district_id'):
                address.district = District.objects.get(pk=data['district_id'])
                address.city = address.district.city
                address.province = address.city.province

        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)
        except District.DoesNotExist:
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)
        except ReceivingAddress.DoesNotExist:
            return Response(err_result(DOES_NOT_EXIST_CODE, u'数据不存在'))
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, event_text + u'收货地址失败').msg)

        if address_id is None and address.is_default is True:
            need_refresh_default_flag = True

        try:
            with transaction.atomic():
                if need_refresh_default_flag is True:
                    ReceivingAddress.objects.filter(is_default=True).update(is_default=False)
                address.save()

            m = err_result(SUCCESS_CODE, event_text + u'收货地址成功').msg
            m['id'] = address.id
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, event_text + u'收货地址失败').msg)

    def delete(self, request, address_id, format=None):
        """
        用户删除自己的收货地址
        :param request:
        :param address_id：收货地址id
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        user = request.user
        try:
            ReceivingAddress.objects.get(pk=address_id, user_id=user.id).delete()
            m = err_result(SUCCESS_CODE, u'删除收货地址成功').msg
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'删除收货地址失败').msg)


class PickupAddressListView(CommonPermissionAPIView):

    def get(self, request, format=None):
        """
        获取用户自己的提货地址列表
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        try:
            user = request.user
            q = UserPickupAddr.objects.filter(user=user).order_by('-is_default','-created_datetime')
            rs = UserPickupAddressSerializer(q, many=True).data

            m = err_result(SUCCESS_CODE, u'获取提货地址成功').msg
            m['data'] = rs
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取提货地址失败').msg)


class PickupAddressView(CommonPermissionAPIView):

    def post(self, request, address_id, format=None):
        """
        用户增加提货点
        :param request:
        :param address_id：提货点id
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        data = request.data
        user = request.user

        try:
            is_default = bool(data['is_default'])
            with transaction.atomic():
                if is_default is True:
                    UserPickupAddr.objects.filter(user=user,is_default=True).update(is_default=False)
                UserPickupAddr(user=user, pickup_addr_id=address_id, is_default=is_default).save()

            m = err_result(SUCCESS_CODE, u'增加提货地址成功').msg
            return Response(m)

        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)
        # except PickupAddr.DoesNotExist:
        #     return Response(err_result(DOES_NOT_EXIST_CODE, u'数据不存在'))
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'增加提货地址失败').msg)

    def delete(self, request, address_id, format=None):
        """
        用户删除提货点
        :param request:
        :param address_id：提货点id
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        user = request.user
        try:
            UserPickupAddr.objects.filter(pickup_addr_id=address_id, user_id=user.id).delete()
            m = err_result(SUCCESS_CODE, u'删除提货地址成功').msg
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'删除提货地址失败').msg)