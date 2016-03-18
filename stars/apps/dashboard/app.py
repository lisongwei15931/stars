import staticpages.urls

from django.conf.urls import url, include

from oscar.core.loading import get_class
from oscar.apps.dashboard.app import DashboardApplication as da

from stars.apps.accounts.decorators import permission_required
from stars.apps.dashboard import views

class DashboardApplication(da):
    ad_app = get_class('dashboard.ad.app', 'application')
    permission_app = get_class('dashboard.permission.app', 'application')
    pickup_admin_app = get_class('dashboard.pickup_admin.app', 'application')
    permissions_map = {}
    business_app = get_class('dashboard.business.app','application')
    dataquery_app = get_class('dashboard.dataquery.app','application')

    login_view = views.LoginView
    logout_view = views.LogoutView

    def get_urls(self):
        # urls = super(DashboardApplication, self).get_urls()
        urls = [
            url(r'^$', permission_required(['dashboard_admin','ISP'])(self.index_view.as_view()), name='index'),
            url(r'^catalogue/', include(self.catalogue_app.urls)),
            url(r'^reports/', include(self.reports_app.urls)),
            url(r'^orders/', include(self.orders_app.urls)),
            url(r'^users/', include(self.users_app.urls)),
            url(r'^content-blocks/', include(self.promotions_app.urls)),
            url(r'^pages/', include(self.pages_app.urls)),
            url(r'^partners/', include(self.partners_app.urls)),
            url(r'^offers/', include(self.offers_app.urls)),
            url(r'^ranges/', include(self.ranges_app.urls)),
            url(r'^reviews/', include(self.reviews_app.urls)),
            url(r'^vouchers/', include(self.vouchers_app.urls)),
            url(r'^comms/', include(self.comms_app.urls)),
            url(r'^shipping/', include(self.shipping_app.urls)),
            url(r'^ad/', include(self.ad_app.urls)),
            url(r'^permission/', include(self.permission_app.urls)),
            url(r'^pickup-admin/', include(self.pickup_admin_app.urls)),
            url(r'^business/', include(self.business_app.urls)),
            url(r'^dataquery/', include(self.dataquery_app.urls)),

            url(r'^login/$', self.login_view.as_view(), name='dashboard-login'),
            url(r'^logout/$', self.logout_view.as_view(), name='dashboard-logout'),

            url(r'^staticpages/', include(staticpages.urls)),
        ]

        return self.post_process_urls(urls)


application = DashboardApplication()
