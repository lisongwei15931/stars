# encoding: utf-8


from django.conf.urls import patterns, url

from oscar.core.application import Application

from stars.apps.dashboard.permission import views
from stars.apps.accounts.decorators import permission_required


class PermissionApplication(Application):
    name = None

    user_list_view = views.UserListView
    user_role_view = views.UserRoleCreateUpdateView

    def get_urls(self):
        urls = [
            url(r'^user-list/$', permission_required(['dashboard_admin'])(self.user_list_view.as_view()), name='user-list'),
            url(r'^user-role/(?P<pk>\d+)/$',
                permission_required([u'dashboard_admin'])(self.user_role_view.as_view()), name='user-role'),
            url(r'^permission-denied/$', views.permission_denied, name='permission-denied'),
        ]
        return self.post_process_urls(patterns('', *urls))


application = PermissionApplication()
