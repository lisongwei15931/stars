# encoding: utf-8


from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.accounts.decorators import permission_required


class PickupAdminApplication(Application):
    name = None

    pickup_store_list_view = get_class('dashboard.pickup_admin.views',
                                       'PickupStoreListView')
    pickup_apply_list_view = get_class('dashboard.pickup_admin.views',
                                       'PickupApplyListView')
    store_income_apply_list_view = get_class('dashboard.pickup_admin.views',
                                             'StoreInComeApplyListView')
    store_income_apply_update_view = get_class('dashboard.pickup_admin.views',
                                               'StoreInComeApplyUpdateView')
    store_income_list_view = get_class('dashboard.pickup_admin.views',
                                       'StoreInComeListView')
    store_income_update_view = get_class('dashboard.pickup_admin.views',
                                         'StoreInComeUpdateView')
    store_income_create_view = get_class('dashboard.pickup_admin.views',
                                         'StoreInComeCreateView')
    pickup_apply_pickup_list_view = get_class('dashboard.pickup_admin.views',
                                              'PickupApplyPickupListView')
    pickup_outcome_deal_view = get_class('dashboard.pickup_admin.views',
                                         'PickupOutcomeDealView')
    pickup_apply_express_list_view = get_class('dashboard.pickup_admin.views',
                                               'PickupApplyExpressListView')
    express_outcome_deal_view = get_class('dashboard.pickup_admin.views',
                                         'ExpressOutcomeDealView')
    pickup_statistics_list_view = get_class('dashboard.pickup_admin.views',
                                            'PickupStatisticsListView')
    login_view = get_class('dashboard.pickup_admin.views',
                           'LoginView')
    def get_urls(self):
        urls = [
            url(r'^pickup-store-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.pickup_store_list_view.as_view()), name='pickup-store-list'),
            url(r'^pickup-apply-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.pickup_apply_list_view.as_view()), name='pickupaddr-pickup-apply-list'),
            url(r'^store-income-apply-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.store_income_apply_list_view.as_view()), name='store-income-apply-list'),
            url(r'^store-income-apply/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.store_income_apply_update_view.as_view()), name='store-income-apply'),
            url(r'^store-income-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff','ISP'])(self.store_income_list_view.as_view()), name='store-income-list'),
            url(r'^store-income-update/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.store_income_update_view.as_view()), name='store-income-update'),
            url(r'^store-income-create/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.store_income_create_view.as_view()), name='store-income-create'),
            url(r'^pickup-apply-pickup-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.pickup_apply_pickup_list_view.as_view()), name='pickup-apply-pickup-list'),
            url(r'^pickup-outcome-deal/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.pickup_outcome_deal_view.as_view()), name='pickup-outcome-deal'),
            url(r'^pickup-apply-express-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.pickup_apply_express_list_view.as_view()), name='pickup-apply-express-list'),
            url(r'^express-outcome-deal/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.express_outcome_deal_view.as_view()), name='express-outcome-deal'),
            url(r'^pickup-statistics-list/$',
                permission_required(['dashboard_admin', 'warehouse_staff'])(self.pickup_statistics_list_view.as_view()), name='pickup-statistics-list'),
            url(r'^pickup-login/$',
                self.login_view.as_view(), name='pickup-login'),
        ]
        return self.post_process_urls(urls)


application = PickupAdminApplication()
