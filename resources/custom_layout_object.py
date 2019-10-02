from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from django.shortcuts import render
from django.template.loader import render_to_string

class VerbalisantFormSection(LayoutObject):
    template = "portal/verbalisanten.html"


    def __init__(self, context_key, template=None):
        self.context_key = context_key
        self.fields = []
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        print(f"context: {context}")
        print(f"form: {form}")
        data = context.get(self.context_key, None)
        return render_to_string(self.template, {'data': data})
