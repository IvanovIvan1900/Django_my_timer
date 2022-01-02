from django.shortcuts import render
from .models import Clients, Tasks
from .forms import FormChangeClient
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q
from .forms import SearchForm
from django.core.paginator import Paginator
from .pref import Pref
from .forms import FormChangeTask

# Create your views here.
def client_list(request):
    keyword = request.GET.get('keyword', '')
    type_of_filter = request.GET.get('search_button', "")
    if type_of_filter == "clear_search":
        keyword = ''
    request.session['client_filter'] = keyword
    client_filter = request.session.get('client_filter', "")
    if client_filter:
        #icontains not workin for sqlite
        q = Q(name__icontains = client_filter.strip()) | \
            Q(full_name__icontains = client_filter.strip())
        # q = Q(name__icontains = client_filter.strip())
        clients = Clients.objects.filter(q).all()
    else:
        clients = Clients.objects.all()
    paginator = Paginator(clients, Pref.get_pref_by_name('client_count_item_on_page', 10))
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    form_search = SearchForm(initial={'keyword': keyword})
    context = {'clients': page.object_list, 'form_search':form_search, 'page':page}
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

def client_delete(request, client_id = ""):
    client = get_object_or_404(Clients, pk=client_id)
    client.delete()
    return HttpResponseRedirect(reverse('my_timer:client_list'))


def task_list(request):
    keyword = request.GET.get('keyword', '')
    type_of_filter = request.GET.get('search_button', "")
    if type_of_filter == "clear_search":
        keyword = ''
    request.session['tasks_filter'] = keyword
    tasks_filter = request.session.get('tasks_filter', "")
    if tasks_filter:
        #icontains not workin for sqlite
        q = Q(name__icontains = tasks_filter.strip()) | \
            Q(client__name__icontains = tasks_filter.strip())
        # q = Q(name__icontains = client_filter.strip())
        tasks = Tasks.objects.filter(q).all()
    else:
        tasks = Tasks.objects.all()
    paginator = Paginator(tasks, Pref.get_pref_by_name('task_count_item_on_page', 10))
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    form_search = SearchForm(initial={'keyword': keyword})
    context = {'tasks': page.object_list, 'form_search':form_search, 'page':page}
    return render(request, 'my_timer_main/main/task_list.html', context)

def task_edit_or_add(request, task_id = ""):
    task = None
    if task_id:
        task = get_object_or_404(Tasks, pk=task_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if task:
            form = FormChangeTask(request.POST, instance=task)
        else:
            form = FormChangeTask(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save(commit=True)
            return HttpResponseRedirect(reverse('my_timer:task_list'))

    # if a GET (or any other method) we'll create a blank form
    else:
        if task:
            form = FormChangeTask(initial={'user': request.user.pk}, instance=task)
        else:
            form = FormChangeTask(initial={'user': request.user.pk})


    return render(request, 'my_timer_main/main/task_edit.html', {'form': form})

def task_delete(request, task_id = ""):
    task = get_object_or_404(Tasks, pk=task_id)
    task.delete()
    return HttpResponseRedirect(reverse('my_timer:task_list'))


# def cleint_filter(request, filter_text):
#     # request.session.
#     request.session['client_filter'] = filter_text
#     return HttpResponseRedirect(reverse('my_timer:client_list'))
