# encoding: utf-8


from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.accounts.decorators import permission_required


class CatalogueApplication(Application):
    name = None
    default_permissions = []
    permissions_map = _map = {}

    product_list_view = get_class('dashboard.catalogue.views',
                                  'ProductListView')
    product_lookup_view = get_class('dashboard.catalogue.views',
                                    'ProductLookupView')
    product_create_redirect_view = get_class('dashboard.catalogue.views',
                                             'ProductCreateRedirectView')
    product_createupdate_view = get_class('dashboard.catalogue.views',
                                          'ProductCreateUpdateView')
    product_delete_view = get_class('dashboard.catalogue.views',
                                    'ProductDeleteView')

    product_class_create_view = get_class('dashboard.catalogue.views',
                                          'ProductClassCreateView')
    product_class_update_view = get_class('dashboard.catalogue.views',
                                          'ProductClassUpdateView')
    product_class_list_view = get_class('dashboard.catalogue.views',
                                        'ProductClassListView')
    product_class_delete_view = get_class('dashboard.catalogue.views',
                                          'ProductClassDeleteView')

    category_list_view = get_class('dashboard.catalogue.views',
                                   'CategoryListView')
    category_detail_list_view = get_class('dashboard.catalogue.views',
                                          'CategoryDetailListView')
    category_create_view = get_class('dashboard.catalogue.views',
                                     'CategoryCreateView')
    category_update_view = get_class('dashboard.catalogue.views',
                                     'CategoryUpdateView')
    category_delete_view = get_class('dashboard.catalogue.views',
                                     'CategoryDeleteView')

    stock_alert_view = get_class('dashboard.catalogue.views',
                                 'StockAlertListView')

    def get_urls(self):
        urls = [
            url(r'^products/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin'])(self.product_createupdate_view.as_view()),
                name='catalogue-product'),
            url(r'^products/create/$',
                permission_required(['dashboard_admin'])(self.product_create_redirect_view.as_view()),
                name='catalogue-product-create'),
            url(r'^products/create/(?P<product_class_slug>[\w-]+)/$',
                permission_required(['dashboard_admin'])(self.product_createupdate_view.as_view()),
                name='catalogue-product-create'),
            url(r'^products/(?P<parent_pk>[-\d]+)/create-variant/$',
                permission_required(['dashboard_admin'])(self.product_createupdate_view.as_view()),
                name='catalogue-product-create-child'),
            url(r'^products/(?P<pk>\d+)/delete/$',
                permission_required(['dashboard_admin'])(None),
                name='catalogue-product-delete'),
            url(r'^$', permission_required(['dashboard_admin'])(self.product_list_view.as_view()),
                name='catalogue-product-list'),
            url(r'^stock-alerts/$', permission_required(['dashboard_admin'])(self.stock_alert_view.as_view()),
                name='stock-alert-list'),
            url(r'^product-lookup/$', permission_required(['dashboard_admin'])(self.product_lookup_view.as_view()),
                name='catalogue-product-lookup'),
            url(r'^categories/$', permission_required(['dashboard_admin'])(self.category_list_view.as_view()),
                name='catalogue-category-list'),
            url(r'^categories/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin'])(self.category_detail_list_view.as_view()),
                name='catalogue-category-detail-list'),
            url(r'^categories/create/$', permission_required(['dashboard_admin'])(self.category_create_view.as_view()),
                name='catalogue-category-create'),
            url(r'^categories/create/(?P<parent>\d+)$',
                permission_required(['dashboard_admin'])(self.category_create_view.as_view()),
                name='catalogue-category-create-child'),
            url(r'^categories/(?P<pk>\d+)/update/$',
                permission_required(['dashboard_admin'])(self.category_update_view.as_view()),
                name='catalogue-category-update'),
            url(r'^categories/(?P<pk>\d+)/delete/$',
                permission_required(['dashboard_admin'])(self.category_delete_view.as_view()),
                name='catalogue-category-delete'),
            url(r'^product-type/create/$',
                permission_required(['dashboard_admin'])(self.product_class_create_view.as_view()),
                name='catalogue-class-create'),
            url(r'^product-types/$',
                permission_required(['dashboard_admin'])(self.product_class_list_view.as_view()),
                name='catalogue-class-list'),
            url(r'^product-type/(?P<pk>\d+)/update/$',
                permission_required(['dashboard_admin'])(self.product_class_update_view.as_view()),
                name='catalogue-class-update'),
            url(r'^product-type/(?P<pk>\d+)/delete/$',
                permission_required(['dashboard_admin'])(self.product_class_delete_view.as_view()),
                name='catalogue-class-delete'),
        ]
        return self.post_process_urls(urls)


application = CatalogueApplication()
