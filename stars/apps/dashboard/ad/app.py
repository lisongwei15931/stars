from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.accounts.decorators import permission_required


class AdDashboardApplication(Application):
    name = None
    default_permissions = ['is_staff', ]
    # permissions_map = _map = {
    #     'rolling-ad': (['is_staff'], ['partner.dashboard_access']),
    #     'rolling-ad-create': (['is_staff'],
    #                                  ['partner.dashboard_access']),
    #     'rolling-ad-list': (['is_staff'], ['partner.dashboard_access']),
    #     'rolling-ad-delete': (['is_staff'],
    #                                  ['partner.dashboard_access']),
    #     'rolling-ad-lookup': (['is_staff'],
    #                                  ['partner.dashboard_access']),
    # }

    # rolling_ad_createupdate_view = get_class('dashboard.ad.views', 'RollingAdCreateUpdateView')
    rolling_ad_create_view = get_class('dashboard.ad.views', 'RollingAdCreateView')
    rolling_ad_update_view = get_class('dashboard.ad.views', 'RollingAdUpdateView')
    rolling_ad_list_view = get_class('dashboard.ad.views', 'RollingAdDetailListView')
    # rolling_ad_detail_list_view = get_class('dashboard.ad.views', 'RollingAdDetailListView')
    rolling_ad_detail_view = get_class('dashboard.ad.views', 'RollingAdDetailView')
    rolling_ad_delete_view = get_class('dashboard.ad.views', 'RollingAdDeleteView')



    def get_urls(self):
        urls = [
                url(r'^rollingad/(?P<pk>\d+)/$', permission_required(['dashboard_admin'])(self.rolling_ad_detail_view.as_view()), name='ad-rolling_ad-detail'),
                url(r'^rollingad/create/$', permission_required(['dashboard_admin'])(self.rolling_ad_create_view.as_view()), name='ad-rolling_ad-create'),
                url(r'^rollingad/(?P<pk>\d+)/update/$', permission_required(['dashboard_admin'])(self.rolling_ad_update_view.as_view()), name='ad-rolling_ad-update'),
                url(r'^rollingad/list/$', permission_required(['dashboard_admin'])(self.rolling_ad_list_view.as_view()), name='ad-rolling_ad-list'),
                url(r'^rollingad/summary/(?P<pk>\d+)/$', permission_required(['dashboard_admin'])(self.rolling_ad_detail_view.as_view()), name='ad-rolling_ad-detail-list'),
                url(r'^rollingad/(?P<pk>\d+)/delete/$', permission_required(['dashboard_admin'])(self.rolling_ad_delete_view.as_view()), name='ad-rolling_ad-delete'),
        ]
        return self.post_process_urls(urls)


application = AdDashboardApplication()
