from django.shortcuts import render
from .models import Clients
from .forms import FormChangeClient
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
# Create your views here.
def client_list(request):
    clients = Clients.objects.all()
    context = {'clients': clients}
    return render(request, 'my_timer_main/main/client_list.html', context)

def client_edit_or_add(request, client_id = ""):
    client = None
    if client_id:
        client = get_object_or_404(Clients, pk=client_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if client:
            form = FormChangeClient(request.POST, instance=client)
        else:
            form = FormChangeClient(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save(commit=True)
            return HttpResponseRedirect(reverse('my_timer:client_list'))

    # if a GET (or any other method) we'll create a blank form
    else:
        if client:
            form = FormChangeClient(initial={'user': request.user.pk}, instance=client)
        else:
            form = FormChangeClient(initial={'user': request.user.pk})


    return render(request, 'my_timer_main/main/client_edit.html', {'form': form})