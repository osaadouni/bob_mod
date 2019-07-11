from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import BobHandelingForm

# Create your views here.
def index_page(request):

    form = BobHandelingForm()
    context = {'form': form}
    return render(request, 'bob/index.html', context)


class CreateApplication(CreateView):
    template_name = 'bob/index.html'
    form_class = BobHandelingForm
