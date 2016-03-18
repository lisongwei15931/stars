# -*- coding: utf-8 -*-s


from django.conf import settings
from django.core.urlresolvers import reverse


class Node(object):
    """
    A node in the dashboard navigation menu
    """

    def __init__(self, label, url_name=None, url_args=None, url_kwargs=None,
                 access_fn=None, icon=None):
        self.label = label
        self.icon = icon
        self.url_name = url_name
        self.url_args = url_args
        self.url_kwargs = url_kwargs
        self.access_fn = access_fn
        self.children = []

    @property
    def is_heading(self):
        return self.url_name is None

    @property
    def url(self):
        return reverse(self.url_name, args=self.url_args,
                       kwargs=self.url_kwargs)

    def add_child(self, node):
        self.children.append(node)

    def is_visible(self, user):
        return self.access_fn is None or self.access_fn(
            user, self.url_name, self.url_args, self.url_kwargs)

    def filter(self, user):
        if not self.is_visible(user):
            return None
        node = Node(
            label=self.label, url_name=self.url_name, url_args=self.url_args,
            url_kwargs=self.url_kwargs, access_fn=self.access_fn,
            icon=self.icon
        )
        for child in self.children:
            if child.is_visible(user):
                node.add_child(child)
        return node

    def has_children(self):
        return len(self.children) > 0


def check_permissions(user, permissions):
    try:
        user_perm = user.userprofile.role
    except:
        return False
    if user_perm in permissions:
        return True
    return False


def default_access_fn(user, url_name, url_args=None, url_kwargs=None):
    if url_name is None:  # it's a heading
        return True
    permissions = settings.PERMISSION_URL_DICT.get(url_name, [])
    return check_permissions(user, permissions)
