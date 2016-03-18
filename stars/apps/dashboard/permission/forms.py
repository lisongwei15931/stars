# encoding: utf-8


from django import forms
from django.forms import (ModelForm, RadioSelect,
                          CheckboxSelectMultiple, TextInput,
                          Select, CheckboxInput)

from oscar.core.loading import get_classes, get_model

UserProfile = get_model('accounts', 'UserProfile')


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('role',)
