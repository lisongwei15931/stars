# -*- coding: utf-8 -*-s

from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from django_tables2 import SingleTableMixin

from oscar.core.loading import get_class, get_model
from tables import RollingAdTable


RollingAd = get_model('ad', 'RollingAd')
RollingAdForm = get_class('dashboard.ad.forms', 'RollingAdForm')


class RollingAdListView(SingleTableMixin, generic.TemplateView):
    template_name = 'dashboard/ad/rolling_ad_list.html'
    model = RollingAd
    table_class = RollingAdTable
    context_table_name = 'rolling_ads'
    form_class = 'RollingAdForm'

    def get_context_data(self, *args, **kwargs):
        ctx = super(RollingAdListView, self).get_context_data(*args, **kwargs)
        ctx['ads'] = self.model.objects.all()
        return ctx


class RollingAdDetailListView(SingleTableMixin,  generic.TemplateView):
    template_name = 'dashboard/ad/rolling_ad_list.html'
    model = RollingAd
    context_object_name = 'rolling_ad'
    table_class = RollingAdTable
    context_table_name = 'ads'
    form_class = 'RollingAdForm'

    def get_table(self, **kwargs):
        table = super(RollingAdDetailListView, self).get_table(**kwargs)
        table.caption = u'轮播广告'
        return table

    def get_table_data(self):
        return self.model.objects.all()

    def get_context_data(self, *args, **kwargs):
        ctx = super(RollingAdDetailListView, self).get_context_data(*args, **kwargs)
        return ctx


class RollingAdDetailView(SingleTableMixin, generic.UpdateView):
    template_name = 'dashboard/ad/rolling_ad_detail.html'
    model = RollingAd
    form_class = RollingAdForm
    context_object_name = 'rolling_ad'
    table_class = RollingAdTable

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class RollingAdCreateView(generic.CreateView):
    template_name = 'dashboard/ad/rolling_ad_update_create.html'
    model = RollingAd
    form_class = RollingAdForm
    context_object_name = 'rolling_ad'
    success_url = reverse_lazy('dashboard:ad-rolling_ad-list')

    def get_object(self):
        return None

    def get_title(self):
        return _("Add a new ad ")

    def get_success_url(self):
        messages.success(self.request, _(u"轮播广告 '%s' 创建") % self.object.title)
        return super(RollingAdCreateView, self).get_success_url()


class RollingAdUpdateView(generic.UpdateView):
    template_name = 'dashboard/ad/rolling_ad_update_create.html'
    model = RollingAd
    form_class = RollingAdForm
    context_object_name = 'rolling_ad'
    success_url = reverse_lazy('dashboard:ad-rolling_ad-list')

    def get_title(self):
        return _("edit a  ad ")


class RollingAdDeleteView(generic.DeleteView):
    template_name = 'dashboard/ad/rolling_ad_delete.html'
    model = RollingAd

    def get_context_data(self, *args, **kwargs):
        ctx = super(RollingAdDeleteView, self).get_context_data(*args, **kwargs)
        ctx['title'] = _("Delete ad '%s'") % self.object.title

    def get_success_url(self):
        messages.info(self.request, _("Ad deleted successfully"))
        return reverse("dashboard:ad-rolling_ad-list")