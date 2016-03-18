# encoding: utf-8



def is_specific_role(user, role_name):

    from stars.apps.accounts.models import UserProfile
    if user.is_anonymous():
        return False
    try:
        current_userprofile = user.userprofile
        current_role = current_userprofile.role
        if current_role == role_name:
            return True
        else:
            return False
    except UserProfile.DoesNotExist:
        return False
