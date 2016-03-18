# coding=utf-8
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class AllowAnyUserAPIView(APIView):
    permission_classes = (AllowAny,)


class CommonPermissionAPIView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )