# -*- coding: utf-8 -*-
#
# from django.shortcuts import render
# from rest_framework.views import APIView
# from oscar.core.compat import get_user_model
# from stars.apps.accounts.models import UserProfile
# from stars.apps.customer.safety.forms import RealNameAuthForm
#
# User = get_user_model()
#
#
# class RealNameAuthView(APIView):
#     def get(self, request, *args, **kwargs):
#         # (0, u'未认证'),(1, u'认证中'),(2, u'认证成功'),(3, u'认证失败')
#         if not hasattr(request.user, 'userprofile'):
#             UserProfile(user=request.user).save()
#
#         form = RealNameAuthForm(instance=request.user.userprofile)
#         tpl = 'customer/safety/real_name_auth/real_name_auth.html'
#         ctx = {'form': form,
#                'frame_id': 'real_name_auth',
#                }
#
#         return render(request, tpl, ctx)
#
#     def post(self, request, *args, **kwargs):
#         form = RealNameAuthForm(request.POST, request.FILES, instance=request.user.userprofile)
#         ctx = {
#                'frame_id': 'real_name_auth',
#                }
#         if form.is_valid():
#             form.save()
#             tpl = 'customer/safety/real_name_auth/submit_suc.html'
#             return render(request, tpl, ctx)
#         else:
#             tpl = 'customer/safety/real_name_auth/real_name_auth.html'
#             ctx['form'] = form
#             return render(request, tpl, ctx)
