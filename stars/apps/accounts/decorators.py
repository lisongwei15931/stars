# encoding: utf-8


from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def permission_required(perm, login_url='dashboard:permission-denied', raise_exception=False):
    def check_perms(user):
        if not isinstance(perm, (list, tuple)):
            perms = (perm, )
        else:
            perms = perm
        if user.is_authenticated():
            try:
                user_perm = user.userprofile.role
            except:
                return False
            if user_perm in perms:
                return True
            if raise_exception:
                raise PermissionDenied
        return False
    return user_passes_test(check_perms, login_url=login_url)
