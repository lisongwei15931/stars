# encoding: utf-8


from django.views import generic
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from oscar.apps.customer.utils import normalise_email
from oscar.core.loading import get_classes, get_model
from oscar.core.compat import get_user_model
from oscar.views import sort_queryset

User = get_user_model()
Partner = get_model('partner', 'Partner')
(
    PartnerSearchForm, PartnerForm, PartnerAddressForm,
    NewUserForm, UserEmailForm, ExistingUserForm
) = get_classes(
    'dashboard.partners.forms',
    ['PartnerSearchForm', 'PartnerForm', 'PartnerAddressForm',
     'NewUserForm', 'UserEmailForm', 'ExistingUserForm'])


class PartnerListView(generic.ListView):
    model = Partner
    context_object_name = 'partners'
    template_name = 'dashboard/partners/partner_list.html'
    form_class = PartnerSearchForm

    def get_queryset(self):
        qs = self.model._default_manager.all()
        qs = sort_queryset(qs, self.request, ['name'])

        self.description = _("All partners")

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['name']:
            qs = qs.filter(name__icontains=data['name'])
            self.description = _("Partners matching '%s'") % data['name']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(PartnerListView, self).get_context_data(**kwargs)
        ctx['queryset_description'] = self.description
        ctx['form'] = self.form
        ctx['is_filtered'] = self.is_filtered
        return ctx


class PartnerUpdateView(generic.UpdateView):
    template_name = 'dashboard/partners/partner_update.html'
    model = Partner
    context_object_name = 'partner'
    form_class = PartnerForm

    def __init__(self, *args, **kwargs):
        super(PartnerUpdateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:partner-list')

    def get_context_data(self, **kwargs):
        context = super(PartnerUpdateView, self).get_context_data(**kwargs)
        return context


class PartnerCreateView(generic.CreateView):
    template_name = 'dashboard/partners/partner_create.html'
    model = Partner
    context_object_name = 'partner'
    form_class = PartnerForm

    def __init__(self, *args, **kwargs):
        super(PartnerCreateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:partner-list')

    def get_context_data(self, **kwargs):
        context = super(PartnerCreateView, self).get_context_data(**kwargs)
        return context
