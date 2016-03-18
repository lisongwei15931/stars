from django.conf import settings


from oscar.core.loading import get_class



Node = get_class('dashboard.nav', 'Node')


def get_nodes(user):
    """
    Return the visible navigation nodes for the passed user
    """
    all_nodes = create_menu(settings.STARS_DASHBOARD_NAVIGATION)
    visible_nodes = []
    for node in all_nodes:
        filtered_node = node.filter(user)
        # don't append headings without children
        if filtered_node and (filtered_node.has_children() or
                              not filtered_node.is_heading):
            visible_nodes.append(filtered_node)
    return visible_nodes

from oscar.apps.dashboard.menu import *
