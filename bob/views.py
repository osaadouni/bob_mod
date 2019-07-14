from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger

from .models import Onderzoek, BobHandeling
from .forms import BOBApplicationForm

# Create your views here.
def index_page(request):

    form = BOBApplicationForm()
    context = {'form': form}
    return render(request, 'bob/index.html', context)


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'bob/home.html'


class BOBApplicationListView(LoginRequiredMixin,ListView):
    model = BobHandeling
    form_class = BOBApplicationForm
    template_name = 'bob/bob_application_list.html'
    ordering = ['-pk']
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        bob_list = BobHandeling.objects.order_by('-pk')
        paginator = Paginator(bob_list, self.paginate_by)
        page = self.request.GET.get('page')
        bob_records = paginator.get_page(page)
        context['object_list'] = bob_records
        return context



class BOBApplicationCreateView(LoginRequiredMixin,CreateView):
    model = BobHandeling
    template_name = 'bob/bob_application_form.html'
    form_class = BOBApplicationForm
    success_url = reverse_lazy('bob:bob-index')

class BOBApplicationDetailView(DetailView):
    model = BobHandeling
    template_name = 'bob/bob_application_detail.html'

class BOBApplicationUpdateView(UpdateView):
    model = BobHandeling
    form_class = BOBApplicationForm
    template_name = 'bob/bob_application_form.html'
    success_url = reverse_lazy('bob:bob-index')


class BOBApplicationDeleteView(DeleteView):
    model = BobHandeling
    template_name = 'bob/bob_application_confirm_delete.html'
    success_url = reverse_lazy('bob:bob-index')
