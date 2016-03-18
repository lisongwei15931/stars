# -*- coding: utf-8 -*-

from stars.apps.customer.safety.common_const import Const


class _ResultCode(Const):
   ERROR_PARAM = 3
   INTERNAL_ERROR = 5
   NO_PERMISSION = 4
   NET_ERROR = 9

   FIN_RETURN_ERROR = 11

   BE_USED = 12

   SUCCESS = 0


ResultCode = _ResultCode()