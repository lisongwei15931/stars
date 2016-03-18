# -*- coding: utf-8 -*-
# import user

# from django.views.generic import View as APIView
from rest_framework.views import APIView

from oscar.core.compat import get_user_model

User = get_user_model()


class UserSummaryView(APIView):
    def get(self, request, *args, **kwargs):
      pass

    def post(self, request, *args, **kwargs):
      pass