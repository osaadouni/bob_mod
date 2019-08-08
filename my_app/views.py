from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse


from .forms import ExampleForm


# Create your views here.
def get_my_form(request):

    if request.method == 'POST':
        form = ExampleForm(request.POST)

        if form.is_valid():

            return HttpResponseRedirect(reverse_lazy('thank-you'))

    else:
        form = ExampleForm()
        form.helper.form_action = reverse('my_app:submit-form')

    return render(request, 'my_app/index.html', {'form': form})



def thank_you(request):

    return HttpResponse('Thank you')
