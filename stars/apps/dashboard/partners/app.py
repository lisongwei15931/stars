# encoding: utf-8


from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class

from stars.apps.accounts.decorators import permission_required


class PartnersDashboardApplication(Application):
    name = None
    default_permissions = []
    permissions_map = _map = {}

    list_view = get_class('dashboard.partners.views', 'PartnerListView')
    create_view = get_class('dashboard.partners.views', 'PartnerCreateView')
    update_view = get_class('dashboard.partners.views', 'PartnerUpdateView')

    def get_urls(self):
        urls = [
            url(r'^$',
                permission_required(['dashboard_admin'])(self.list_view.as_view()),
                name='partner-list'),
            url(r'^create/$',
                permission_required(['dashboard_admin'])(self.create_view.as_view()),
                name='partner-create'),
            url(r'^update/(?P<pk>\d+)/$',
                permission_required(['dashboard_admin'])(self.update_view.as_view()),
                name='partner-update'),
        ]
        return self.post_process_urls(urls)


application = PartnersDashboardApplication()
