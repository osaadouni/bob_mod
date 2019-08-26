from django_tables2 import tables, TemplateColumn
from django.utils.safestring import mark_safe
from django.utils.html import escape

from .models import BOBAanvraag
from .transitions import STATE_CSS, STATE_HUMAN

class BOBAanvraagTable(tables.Table):
    class Meta:
        model = BOBAanvraag
        #template_name = 'django_tables2/bootstrap-responsive.html'
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'status', 'dvom_aanvraagpv', 'dvom_datumpv', 'dvom_verbalisant','dvom_verbalisantcontactgegevens', 'created_by', 'updated_by', 'actie')


        attrs = {
            'th': {
                '_ordering': {
                    'orderable': 'sortable',
                    'ascending': 'ascend',
                    'descending': 'descend'
                },
                'class': 'p-2'
            },
            'td': {
                'class': 'p-2'
            },
            'class': 'table-bordered table-striped table-condensed table-responsive mb-3 mt-3 w-100'
        }

    actie = TemplateColumn(template_name='resources/bobaanvraag_action_column.html')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
    def render_status(self, value):
        css = STATE_CSS.get(value, value)
        value = STATE_HUMAN.get(value, value)
        print(f"{value} - {css}")
        return mark_safe('<span class="badge %s p-1">%s</span>' % (css, escape(value)))
