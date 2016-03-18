# -*- coding: utf-8 -*-s

from django.contrib.auth import logout


class RoleFrontCheckMiddleware(object):
    def process_request(self, request):
        user = request.user
        if user.is_authenticated():
            if 'dashboard' not in request.path:
                try:
                    userprofile = user.userprofile
                    if userprofile.is_warehouse_staff():
                        logout(request)
                    if userprofile.is_ISP():
                        logout(request)
                except:
                    pass
