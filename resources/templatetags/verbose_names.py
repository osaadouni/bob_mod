from django import template

register = template.Library()

@register.filter(name='get_field_verbose_name')
def get_field_verbose_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name #.itle()


