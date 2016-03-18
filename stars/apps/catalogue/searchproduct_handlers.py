#coding=utf-8
'''
'''
from django.views.generic.list import MultipleObjectMixin
from django.conf import settings
from stars.apps.catalogue.models import Product,Category,ProductAttributeValue
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Q,Sum
import datetime
from pycparser import c_generator
import re
class SimpleProductSearchHandler(MultipleObjectMixin):
    """
    修改了is_on_shelves = True
    """
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, request_data, full_path, categories=None):
        self.categories = categories
        self.kwargs = {'page': request_data.get('page', 1),
                       'category': request_data.get('category', ''),
                       'price': request_data.get('price', ''),
                       'alcoholicity': request_data.get('alcoholicity', ''),
                       'jgpx': request_data.get('jgpx', ''),
                       'xiaoliang': request_data.get('xiaoliang', ''),
                       'xiaoprice': request_data.get('xiaoprice', ''),
                       'daprice' : request_data.get('daprice', ''),
                       'search_q' : request_data.get('q', ''),
                       'search_q1': request_data.get('q1', ''),
                       }
        
        self.attribute_kw = {}
        if self.kwargs['category']:
            c_g = self.current_category = get_object_or_404(Category,name=self.kwargs['category'])
            self.current_category = c_g
            if c_g.product_class:
                for p_class in c_g.get_product_class():
                    self.attribute_kw[p_class.code] = request_data.get(p_class.code, '')
        else :
            self.current_category = None
            self.attribute_kw = {}
        

        
        
        self.object_list = self.get_queryset()

    def get_queryset(self):
        qs = Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.datetime.now().date())
        if self.categories:
            qs = qs.filter(categories__in=self.categories).distinct()
        
        categoryname = self.kwargs['category']
        if categoryname:
            category = get_object_or_404(Category,name=categoryname)
            child_category = category.get_descendants_and_self()
            qs = qs.filter(categories__in=child_category)
            
            if not qs:
                return qs
        
        price = self.kwargs['price']
        try:
            xiaoprice = float(self.kwargs['xiaoprice'])
            if not xiaoprice:
                xiaoprice = 0
        except:
            xiaoprice = 0
        try:
            daprice = float(self.kwargs['daprice'])
            if not daprice:
                daprice = 99999999
        except:
            daprice = 99999999
        
        price_sql = '''
            select p_price  from (select p.id,
            case when hq.strike_price is not null  then hq.strike_price 
                 when cj.unit_price is not null then cj.unit_price*(1+ss.ud_up_range)
                 when ss.opening_price is not null then  ss.opening_price*(1+ss.ud_up_range) 
                 else 99999999 end as p_price
            from catalogue_product p 
            left join
            (
            select c1.product_id,c1.unit_price from 
            (select product_id,unit_price ,created_datetime from commission_tradecomplete 
            group by product_id,created_datetime)c1 
            join
            (select product_id,max(created_datetime) created_datetime from commission_tradecomplete 
            group by product_id ) c2 
            on c1.product_id = c2.product_id
            and c1.created_datetime = c2.created_datetime 
            )cj
            on p.id = cj.product_id
            left join 
            (
            select c1.product_id,c1.strike_price from commission_stockticker c1 
            join
            (select product_id,max(created_datetime) created_datetime from commission_stockticker 
            group by product_id ) c2 
            on c1.product_id = c2.product_id
            and c1.created_datetime = c2.created_datetime
            )hq
            on p.id = hq.product_id
            left join 
            (
            select g.product_id,g.opening_price,g.ud_up_range from commission_stockproductconfig g
            ) ss 
            on p.id = ss.product_id
            )pp
            where pp.id = catalogue_product.id
        '''
        
        if price and price != '':
            price_range = price.split('-')
            if len(price_range) == 2:
                min_price = int(price_range[0])
                max_price = int(price_range[1])
            else :
                min_price = int(re.split(r'\W+', price)[0])
                max_price = 99999999
            price_sql_where = '('+ price_sql+')'+' between %d and %d ' %(min_price, max_price)
            qs = qs.extra(select={'p_price': price_sql}, where=[price_sql_where])

        elif price == '' or not price:
            if self.kwargs['xiaoprice'] or self.kwargs['daprice']:
                min_price = xiaoprice
                max_price = daprice
                price_sql_where = '('+ price_sql+')'+' between %d and %d'%(min_price,max_price)  
                qs = qs.extra(select={'p_price': price_sql}, where=[price_sql_where])
        else :
            pass

    
        alcoholicity_range = self.kwargs['alcoholicity']
        if alcoholicity_range:
            if u'以下' in  alcoholicity_range:
                min_alcoholicity = 0
                max_alcoholicity = int(alcoholicity_range[:2])
            elif u'以上' in  alcoholicity_range:
                max_alcoholicity = 999
                min_alcoholicity = int(alcoholicity_range[:2])
            else:
                min_alcoholicity = int(alcoholicity_range[:2])
                max_alcoholicity = int(alcoholicity_range[3:5])
            
            attr = ProductAttributeValue.objects.filter(attribute__code='degree').filter(value_text__gte=min_alcoholicity).filter(
                                                                                           value_text__lte=max_alcoholicity)
            qs = qs.filter(attribute_values__in=attr)
        
        jgpx = self.kwargs['jgpx']
        
        if jgpx == 'DESC':
            qs = qs.extra(select={'p_price': price_sql}).order_by('-p_price')
        if jgpx == 'ASC':
            qs = qs.extra(select={'p_price': price_sql}).order_by('p_price')
                
        search_q = self.kwargs['search_q'] 
        search_q1 = self.kwargs['search_q1']
        if search_q and search_q != u'输入商品名、货号、商品关键字':
            qs = qs.filter(Q(title__icontains=search_q)|Q(description__icontains=search_q)
                            |Q(upc__icontains=search_q)|Q(categories__name__icontains=search_q)
                            |Q(product_class__name__icontains=search_q)|Q(attribute_values__value_text__icontains=search_q)
                            ).distinct()
        if search_q1:
            qs = qs.filter(Q(title__icontains=search_q1)|Q(description__icontains=search_q1)
                            |Q(upc__icontains=search_q1)|Q(categories__name__icontains=search_q1)
                            |Q(product_class__name__icontains=search_q1)|Q(attribute_values__value_text__icontains=search_q1)
                            ).distinct()
            
        if self.attribute_kw:
            for (k, v) in self.attribute_kw.iteritems():
                if v:
                    if u'度以下'  in v or u'ML以下' in v:
                        v = int(re.split(r'[a-zA-Z\W]+', v)[0])
                        attr = ProductAttributeValue.objects.filter(attribute__code=k).filter(value_text__lte=v)
                    elif u'度以上' in v or u'ML以上' in v:
                        v = int(re.split(r'[a-zA-Z\W]+', v)[0])
                        attr = ProductAttributeValue.objects.filter(attribute__code=k).filter(value_text__gte=v)
                    elif u'-' in v:
                        min_v = int(re.split(r'[a-zA-Z\W]+', v)[0])
                        max_v = int(re.split(r'[a-zA-Z\W]+', v)[1])
                        attr = ProductAttributeValue.objects.filter(attribute__code=k).filter(value_text__gte=min_v,
                                                                                                value_text__lte=max_v)
                    else :
                        attr = ProductAttributeValue.objects.filter(attribute__code=k).filter(value_text=v)
                    qs = qs.filter(attribute_values__in=attr)

        xiaoliang = self.kwargs['xiaoliang']
        pq = qs.annotate(q=Sum('trade_complete_product__quantity'))
        if xiaoliang == 'DESC':
            qs = pq.order_by('-q')
        if xiaoliang == 'ASC':
            qs = pq.order_by('q')    
        return qs
    
    def get_count(self):
        return self.get_queryset().count()
    
    def get_search_context_data(self, context_object_name):
        # Set the context_object_name instance property as it's needed
        # internally by MultipleObjectMixin
        self.context_object_name = context_object_name
        context = self.get_context_data(object_list=self.object_list)
        context[context_object_name] = context['page_obj'].object_list
        context['kwargs'] = self.kwargs
        context['count'] = self.get_count()
        context['attribute_kw'] = self.attribute_kw
        
        context['category'] = self.current_category
        context['category_all'] = get_list_or_404(Category,depth=1)
        return context
