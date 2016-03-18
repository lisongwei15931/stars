# -*- coding: utf-8 -*-s

from django.views.generic import UpdateView, ListView, CreateView, DeleteView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect

from oscar.core.loading import get_classes, get_model


(UserRoleForm, ) \
    = get_classes('stars.apps.dashboard.permission.forms',
                  ('UserRoleForm', ))

UserProfile = get_model('accounts', 'UserProfile')


class UserListView(ListView):
    template_name = 'dashboard/permission/user_list.html'
    paginate_by = 20
    context_object_name = 'user_list'

    def get_queryset(self):
        if self.kw_word:
            queryset = User.objects.filter(username__contains=self.kw_word).order_by('-id')
        else:
            queryset = User.objects.all().order_by('-id')
        return queryset


    def get(self, request, *args, **kwargs):
        self.kw_word =  request.GET.get('kw_word')
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        context = self.get_context_data()
        context['kw_word'] = self.kw_word
        return self.render_to_response(context)


class UserRoleCreateUpdateView(UpdateView):

    template_name = 'dashboard/permission/user_role.html'
    model = UserProfile
    context_object_name = 'user_permission_group'
    form_class = UserRoleForm

    def __init__(self, *args, **kwargs):
        super(UserRoleCreateUpdateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:user-list')

    def get_context_data(self, **kwargs):
        ctx = super(UserRoleCreateUpdateView, self).get_context_data(**kwargs)
        ctx['current_user'] = self.object.user
        ctx['request'] = self.request
        return ctx


def permission_denied(request):
    user = request.user
    try:
        current_userprofile = user.userprofile
        if current_userprofile.is_dashboard_admin():
            return redirect('dashboard:dashboard-login')
        elif current_userprofile.is_warehouse_staff():
            return redirect('dashboard:pickup-login')
        elif current_userprofile.is_member_unit():
            return redirect('dashboard:business-login')
        elif current_userprofile.is_trader():
            return redirect('dashboard:trader-login')
        else:
            return HttpResponse(u'您没有进行此操作的权限。')
    except:
        return HttpResponse(u'您没有进行此操作的权限。')
