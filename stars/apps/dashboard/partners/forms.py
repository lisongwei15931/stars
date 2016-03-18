# encoding: utf-8


from django import forms
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.db.models.query_utils import Q

from oscar.core.loading import get_model
from oscar.core.compat import get_user_model

from stars.apps.pickup_admin.models import APPLY_STATUS


Partner = get_model('partner', 'Partner')
User = get_user_model()


class PartnerSearchForm(forms.Form):
    name = forms.CharField(required=False, label=u'名字')
    user = forms.CharField(required=False, label=u'用户')


class PartnerForm(forms.ModelForm):

    class Meta:
        model = Partner
        exclude = []

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        name_field = self.fields['name']
        name_field.label = u'名字'
        # filter users
        users_field = self.fields['users']
        if self.instance:
            available_users = User.objects.filter(Q(partners__isnull=True)|Q(partners=self.instance)).distinct()
        else:
            available_users = User.objects.filter(partners__isnull=True)
        users_field.queryset = available_users
        users_field.label = u'关联的用户'
