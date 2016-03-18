from django.conf.urls import url, include
from oscar.apps.catalogue.reviews.app import application as reviews_app
from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.catalogue.views import get_province_citys,city_has_product


class BaseCatalogueApplication(Application):
    name = 'catalogue'
    detail_view = get_class('catalogue.views', 'ProductDetailView')
    catalogue_view = get_class('catalogue.views', 'CatalogueView')
    category_view = get_class('catalogue.views', 'ProductCategoryView')
    range_view = get_class('offer.views', 'RangeDetailView')
    custom_detail_view = get_class('catalogue.views', 'CustomProductDetailView')
    all_product_view = get_class('catalogue.views','AllSearchProductView')


    def get_urls(self):
        urlpatterns = super(BaseCatalogueApplication, self).get_urls()
        urlpatterns += [
            # url(r'^$', self.catalogue_view.as_view(), name='index'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.custom_detail_view.as_view(), name='detail'),
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                self.category_view.as_view(), name='category'),
            # Fallback URL if a user chops of the last part of the URL
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)/$',
                self.category_view.as_view()),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range'),
            url(r'^searchproducts/$',self.all_product_view.as_view(),name='allproducts'),
            url(r'^get_province_citys/(?P<pid>\d+)/$', get_province_citys, name='get_province_citys'),
            url(r'^city_has_product/$', city_has_product, name='city_has_product'),
                        ]
        return self.post_process_urls(urlpatterns)


class ReviewsApplication(Application):
    name = None
    reviews_app = reviews_app

    def get_urls(self):
        urlpatterns = super(ReviewsApplication, self).get_urls()
        urlpatterns += [
            url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/reviews/',
                include(self.reviews_app.urls)),
        ]
        return self.post_process_urls(urlpatterns)


class CatalogueApplication(BaseCatalogueApplication, ReviewsApplication):
    """
    Composite class combining Products with Reviews
    """


application = CatalogueApplication()
