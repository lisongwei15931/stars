# coding=utf-8

SUCCESS_CODE = 199
SYSTEM_ERR_CODE = 115
DOES_NOT_EXIST_CODE = 114
ERROR_PARAM = 113
NO_PERMISSION = 116

class err_result:
    _code = 0
    _detail = 'unknown'

    def __init__(self, code, msg=''):
        self._detail = msg
        self._code = code

    def __str__(self):
        return "{'code':" + str(self._code) + ", 'msg': '" + self._detail + "'}"

    @property
    def data(self):
        return {'code':self._code, 'msg': self._detail}

    @property
    def msg(self):
        return self.data