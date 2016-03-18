from django.conf.urls import url
from oscar.apps.promotions.models import PagePromotion, KeywordPromotion
from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.promotions.views import tend_view


class PromotionsApplication(Application):
    name = 'promotions'
    home_view = get_class('promotions.views', 'HomeView')
    record_click_view = get_class('promotions.views', 'RecordClickView')
    search_view = get_class('promotions.views', 'SearchView')
    today_new_view = get_class('promotions.views', 'TodayNewView')
    news_prodct = get_class('promotions.views', 'NewsProductView')
    news_prodct_detail = get_class('promotions.views', 'NewsProductDetailView')
    brand_gather = get_class('promotions.views','BrandGatherView')

    def get_urls(self):
        urls = [
            url(r'page-redirect/(?P<page_promotion_id>\d+)/$',
                self.record_click_view.as_view(model=PagePromotion),
                name='page-click'),
            url(r'keyword-redirect/(?P<keyword_promotion_id>\d+)/$',
                self.record_click_view.as_view(model=KeywordPromotion),
                name='keyword-click'),

            url(r'^$', self.home_view.as_view(), name='home'),
            url(r'^search_form/$', self.search_view.as_view(), name='search_form'),
            url(r'^tend-view/(?P<pid>\d+)/$', tend_view, name='tend_view'),
            url(r'^today/new/$', self.today_new_view.as_view(), name='today_new_view'),
            url(r'^news/product/$', self.news_prodct.as_view(), name='news_product'),
            url(r'^news/product/(?P<pk>\d+)/$', self.news_prodct_detail.as_view(), name='news_product_detail'),
            url(r'^brandgather/product/$', self.brand_gather.as_view(), name='brandgather_product'),
        ]
        return self.post_process_urls(urls)


application = PromotionsApplication()
