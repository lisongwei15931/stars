# coding=utf-8
import logging
from datetime import datetime

from django.db.models import Q
from rest_framework.response import Response

from stars.apps.api.common.views import AllowAnyUserAPIView
from stars.apps.api.error_result import err_result, SUCCESS_CODE, SYSTEM_ERR_CODE, DOES_NOT_EXIST_CODE, ERROR_PARAM
from stars.apps.api.serializers import ProductSimpleSerializer, ProductSearchResultSerializer
from stars.apps.catalogue.models import Category
from stars.apps.commission.models import Product


class CategoryProductListView(AllowAnyUserAPIView):

    def get(self, request, category_id, format=None):
        """
        获取指定category_id下的商品信息
        :param request:
        :param category_id:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        try:

            ps = Category.objects.get(pk=category_id).get_category_products()
            r = []
            for p in ps:
                r.append(ProductSimpleSerializer(p).data)

            m = err_result(SUCCESS_CODE, u'获取商品分类成功').msg
            m['data'] = r
            return Response(m)
        except Category.DoesNotExist:
            return Response(err_result(DOES_NOT_EXIST_CODE, u'数据不存在'))
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'获取商品分类失败').msg)


class ProductSearchView(AllowAnyUserAPIView):
    __row_per_page = 10

    def get(self, request, format=None):
        """
        搜索商品
        :param request:
        :param format:
        :return: SUCCESS_CODE:'成功’;SYSTEM_ERR_CODE:系统错误.
        """
        data = request.GET
        try:
            page_offset = int(data.get('page', 1))
            row_per_page = int(data.get('num', self.__row_per_page))
            if page_offset < 1 or row_per_page < 1:
                raise ValueError
            page_offset -= 1
        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)
        try:

            start_time = datetime.now()
            qs = Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.today().date())
            if data.get('product_id'):
                qs = qs.filter(pk_in=data.get('product_id'))

            if data.get('q'):
                q = data.get('q')
                qs = qs.filter(Q(title__icontains=q)|Q(description__icontains=q)
                            |Q(upc__icontains=q)|Q(categories__name__icontains=q)
                            |Q(product_class__name__icontains=q)|Q(attribute_values__value_text__icontains=q)
                            )
            qs = qs.distinct()
            count = qs.count()

            rs = []
            for r in qs[page_offset*row_per_page: (page_offset*row_per_page)+row_per_page]:
                rs.append(ProductSearchResultSerializer(r).data)

            end_time = datetime.now()
            time_diff = (end_time-start_time).total_seconds()

            m = err_result(SUCCESS_CODE, u'获取商品规格成功').msg
            m['time_used'] = time_diff
            m['num'] = row_per_page
            m['found'] = count
            m['total_page'] = int((count+row_per_page-1)/row_per_page)
            m['current_page'] = page_offset + 1
            m['next_page'] = min(page_offset + 2, m['total_page'])
            m['data'] = rs
            m['current_time'] = datetime.today()
            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'搜索商品失败').msg)
