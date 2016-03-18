# -*- coding: utf-8 -*-
import logging

from django.db import transaction
from rest_framework.response import Response

from oscar.core.loading import get_model
from stars.apps.api.common.views import CommonPermissionAPIView
from stars.apps.api.error_result import SYSTEM_ERR_CODE, err_result, SUCCESS_CODE, ERROR_PARAM
from stars.apps.api.serializers import WishLineProductSerializer
from stars.apps.catalogue.models import Product

WishList = get_model('wishlists', 'WishList')
WishLine = get_model('wishlists', 'Line')
BasketItem = get_model('basket', 'Line')


class AppMyFavListView(CommonPermissionAPIView):
    __DEFAULT_ROW_PER_PAGE = 20

    def get(self, request, *args, **kwargs):
        """
        获取我的关注列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        data = request.GET
        try:
            page_offset = int(data.get('page', 1))
            row_per_page = int(data.get('num', self.__DEFAULT_ROW_PER_PAGE))
            if row_per_page < 1 or page_offset < 1:
                raise ValueError
        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)

        m = err_result(SUCCESS_CODE,  u'获取关注成功').msg
        m['page_count'] = 0
        m['page_index'] = page_offset

        try:
            wishlist = WishList.objects.filter(owner__pk=user.pk).first()
            if not wishlist:
                wishlist = WishList(owner=user)
                wishlist.save()
                m['data'] = []
            else:
                query = WishLine.objects.select_related('product').filter(wishlist=wishlist,
                                                product__is_on_shelves=True,
                                                )
                count = query.count()
                m['page_count'] = (count+row_per_page-1) // row_per_page
                ps = query[(page_offset-1)*row_per_page: page_offset*row_per_page]

                m['data'] = WishLineProductSerializer(ps, many=True).data

            m['next_page_index'] = min(m['page_index']+1, m['page_count'])

            return Response(m)
        except Exception as e:
            logging.exception(e)

            return Response(err_result(SYSTEM_ERR_CODE, u'获取关注失败').msg)

    def post(self, request, *args, **kwargs):
            """
            添加商品到我的关注
            :param request:
            :param args:
            :param kwargs:
            :return:
            """
            user = request.user
            ids = request.data['product_ids']
            flag = int(request.data.get('remove_from_basket_flag', 0))
            try:
                if isinstance(ids, (unicode, str)):
                    ids = ids.split(',')
                wish_list, _ = WishList.objects.get_or_create(owner=user)
                with transaction.atomic():
                    for p in Product.objects.filter(pk__in=ids):
                        wish_list.add(p)

                    if flag == 1:
                        BasketItem.objects.filter(product_id__in=ids, basket__owner=user, basket__status='Open').delete()
                # basket.lines

                return Response(err_result(SUCCESS_CODE,  u'关注成功').msg)
            except Exception as e:
                logging.exception(e)
                return Response(err_result(SYSTEM_ERR_CODE, u'关注失败').msg)


class AppMyFavProduct(CommonPermissionAPIView):

    def post(self, request, product_pk, *args, **kwargs):
        """
        添加商品到我的关注
        :param request:
        :param product_pk:  商品id
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        try:
            product = Product.objects.get(pk=product_pk)
            wishlist, _ = WishList.objects.get_or_create(owner=user)
            wishlist.add(product)
            return Response(err_result(SUCCESS_CODE,  u'关注成功').msg)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'关注失败').msg)

    def delete(self, request, product_pk, format=None):
        """
        从我的关注里删除关注商品
        :param request:
        :param product_pk：商品id
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """

        try:
            WishLine.objects.filter(wishlist__owner=request.user, product__pk=product_pk).delete()
            m = err_result(SUCCESS_CODE, u'取消关注成功').msg
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'取消关注失败').msg)