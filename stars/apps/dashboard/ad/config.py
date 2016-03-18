from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AdDashboardConfig(AppConfig):
    # label = 'ad_dashboard'
    name = 'stars.apps.dashboard.ad'
    verbose_name = _('Ad dashboard')
