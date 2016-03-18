# -*- coding: utf-8 -*-s

from django.views import generic

from oscar.core.loading import get_class, get_model

RollingAd = get_model('ad', 'RollingAd')
RollingAdForm = get_class('dashboard.ad.forms', 'RollingAdForm')


class RollingAdListView(generic.TemplateView):
    template_name = 'dashboard/ad/rolling_ad_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(self.__class__, self).get_context_data(**kwargs)

        ctx['rolling_ad_list'] = RollingAd.objects.all()

        return ctx
