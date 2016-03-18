# encoding: utf-8


from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.views.generic import FormView, RedirectView, TemplateView

from oscar.core.loading import get_model
from oscar.core.compat import get_user_model

from stars.apps.dashboard.forms import LoginForm


class LoginView(FormView):
    template_name = 'dashboard/dashboard_login.html'
    form_class = LoginForm

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        response = HttpResponseRedirect(self.request.GET.get('next', '/dashboard/'))
        return response


class LogoutView(RedirectView):
    url = '/dashboard/login/'
    permanent = False

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        response = super(LogoutView, self).get(request, *args, **kwargs)

        return response
