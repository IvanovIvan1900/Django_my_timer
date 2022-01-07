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
from .models import TimeTrack
from django.db import connection
from django.http import HttpResponse
from django.utils import timezone as tz
from .forms import FormNewTask
from django.utils.dateparse import parse_datetime
from django.utils.timezone import get_current_timezone
from .forms import FromChangeTimeTracker

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
            form = FormCha(request.POST, instance=task)
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

def task_delete(request, task_id):
    task = get_object_or_404(Tasks, pk=task_id)
    task.delete()
    return HttpResponseRedirect(reverse('my_timer:task_list'))



def work_place(request):
    # last_tasks = Tasks.objects.
    def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def get_last_task(count_last_tasks:int):
        """Возвращает словарь данных последних активных задач. Возвращаются только активные задачи:
        Args:
            count_last_tasks (int): Количество последних задач

        Returns:
        Словарь, содержащий
            task_id
            max_date
            task_name
            task_is_acitve
            client_name
            client_id
            task_duration
            diff_day - сколько дней назад последний раз работали с задачей
        """
        dic_of_data = {}
        tz_curr = get_current_timezone()
        with connection.cursor() as cursor:
            cursor.execute("""SELECT last_tasks.task_id as task_id, last_tasks.duration as task_duration, last_tasks.max_date as max_date, main_tasks.name as task_name, 
            main_tasks.is_active as task_is_acitve, main_clients.name as client_name,  main_clients.id as client_id FROM
                    (SELECT task_id, max(date_stop) as max_date, SUM(duration_sec) as duration from main_timetrack group BY task_id) as last_tasks LEFT JOIN
                    main_tasks on last_tasks.task_id = main_tasks.id LEFT JOIN main_clients on main_tasks.client_id = main_clients.id
                    WHERE main_tasks.is_active = 1 ORDER BY max_date DESC limit %s""", [count_last_tasks])
            dic_of_data = dictfetchall(cursor)
            # разницу рассчитаем вручную, т.к.в разных типах БД разные функции
            for elem in dic_of_data:
                elem['diff_day'] = ''
                max_date = parse_datetime(elem['max_date'])
                max_date = max_date.replace(tzinfo=tz_curr)
                if max_date:
                    elem['diff_day'] = (tz.now().date() - max_date.date()).days
                
        return dic_of_data
    
    message = ""
    
    if request.method == 'POST':
        task_to_start = None
        task_name = request.POST.get('task')
        client_id = request.POST.get('client')
        client = Clients.objects.get(pk = client_id)
        task = Tasks.objects.filter(name__icontains=task_name, client=client)
        if task.count() == 1:
            task_to_start = task[0]
        elif task.count() > 1:
            message = "По данному клиенту уже есть такая задача, запустите ее из списка задач"
        else:
            task_to_start = Tasks(name=task_name, client=client, is_active=True, user=request.user)
            task_to_start.save()
        
        if task_to_start is not None:
            action_wich_tasks(request=request, action="start", id=task_to_start.pk)

    array_dic_of_data_last_tasks = get_last_task(Pref.get_pref_by_name('work_place_count_last_task', 10))
    active_time_treket = TimeTrack.objects.filter(is_active = True).order_by('-date_start')

    keyword  = ''
    form_search = SearchForm(initial={'keyword': keyword})
    form_new_task = FormNewTask()
    context = {'array_dic_of_data_last_tasks': array_dic_of_data_last_tasks,'form_search':form_search, 'active_time_treket':active_time_treket,
            'form_new_task':form_new_task ,}
    return render(request, 'my_timer_main/main/work_place.html', context)

def action_wich_tasks(request, action, id):
    """Выполняет действия с задачей

    Args:
        request ([type]): [description]
        action ([str]): описание действия (start, stop)
        id ([int]): идентификатор, если действие start - идентификатор task, если действие stop - идентификатор time_tracker
    """
    if action == "start":
        task = get_object_or_404(Tasks, pk=id)
        new_tm = TimeTrack(task = task, date_start = tz.now(), user = request.user, duration_sec = 0)
        new_tm.save()
    elif action == "stop":
        time_track = get_object_or_404(TimeTrack, pk=id)
        time_track.date_stop = tz.now()
        time_track.save()
    else:
        return HttpResponse(f'action "{action}" not possible')

    
    return HttpResponseRedirect(reverse('my_timer:work_place'))
# def cleint_filter(request, filter_text):
#     # request.session.
#     request.session['client_filter'] = filter_text
#     return HttpResponseRedirect(reverse('my_timer:client_list'))

def time_track_list(request):
    keyword = ''
    # keyword = request.GET.get('keyword', '')
    # type_of_filter = request.GET.get('search_button', "")
    # if type_of_filter == "clear_search":
    #     keyword = ''
    # request.session['client_filter'] = keyword
    # client_filter = request.session.get('client_filter', "")
    # if client_filter:
    #     #icontains not workin for sqlite
    #     q = Q(name__icontains = client_filter.strip()) | \
    #         Q(full_name__icontains = client_filter.strip())
    #     # q = Q(name__icontains = client_filter.strip())
    #     clients = Clients.objects.filter(q).all()
    # else:
    #     clients = Clients.objects.all()
    # paginator = Paginator(clients, Pref.get_pref_by_name('client_count_item_on_page', 10))
    # if 'page' in request.GET:
    #     page_num = request.GET['page']
    # else:
    #     page_num = 1
    # page = paginator.get_page(page_num)
    time_trackers = TimeTrack.objects.all()
    form_search = SearchForm(initial={'keyword': keyword})
    context = {'time_trackers': time_trackers, 'form_search':form_search, }
    return render(request, 'my_timer_main/main/time_track_list.html', context)

def time_track_edit_or_add(request, time_track_id = ""):
    time_track = None
    if time_track_id:
        time_track = get_object_or_404(TimeTrack, pk=time_track_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if time_track:
            form = FromChangeTimeTracker(request.POST, instance=time_track)
        else:
            form = FromChangeTimeTracker(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save(commit=True)
            return HttpResponseRedirect(reverse('my_timer:time_track_list'))

    # if a GET (or any other method) we'll create a blank form
    else:
        if time_track:
            form = FromChangeTimeTracker(initial={'user': request.user.pk}, instance=time_track)
        else:
            form = FromChangeTimeTracker(initial={'user': request.user.pk})


    return render(request, 'my_timer_main/main/time_track_edit.html', {'form': form})

