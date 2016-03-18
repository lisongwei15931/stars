from django import template

register = template.Library()


@register.filter
def has_focused_by(product, user):
    return product and product.has_focused_by(user)