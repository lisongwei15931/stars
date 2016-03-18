from django import template
from django.forms.fields import ImageField


register = template.Library()
@register.filter
def is_image_field(o):
    return isinstance(o, ImageField)

@register.filter
def order_by(queryset, args):
    return queryset.order_by(args)


@register.filter()
def multiply(a,b):
    try:
        return float(a) * float(b)
    except Exception:
        return ''
    
@register.filter
def get_dictvalue(value,key):
    try:
        return value[key]
    except:
        return ''

@register.filter
def max_num(product,user):
    try:
       return product.get_max_canbuy_num(user)   
    except:
        pass
    
    
