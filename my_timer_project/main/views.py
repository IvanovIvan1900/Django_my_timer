import datetime
from asyncio import Task
from datetime import datetime as dt
from operator import itemgetter

import pytz
# from .forms import FormTestWidget
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import caches
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import F, Max, Q, Subquery, Sum, Value
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone as tz
from django.utils.dateparse import parse_datetime
from django.utils.timezone import get_current_timezone
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView, ProcessFormView, UpdateView


from .forms import (FormChangeClient, FormChangeTask, FormCommentEdit,
                    FormNewTask, FormTameTrackerFilter, FormWokrPlaceFilter,
                    FromChangeTimeTracker, SearchForm, FormTasksFilter)

from .models import Clients, Comments, Tasks, TimeTrack
from .pref import Pref
from .utility import count_active_task_add, count_active_task_minus, date_convert_from_string, date_end_of_day, log_exception
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
@log_exception(None)
@login_required
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

@log_exception(None)
@login_required
def client_edit_or_add(request, client_id = ""):
    client = None
    client = get_object_or_404(Clients, pk=client_id) if client_id else None
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
        else:
            return render(request, 'my_timer_main/main/client_edit.html', {'form': form})            
    # if a GET (or any other method) we'll create a blank form
    else:
        if client:
            form = FormChangeClient(initial={'user': request.user.pk}, instance=client)
        else:
            form = FormChangeClient(initial={'user': request.user.pk, 'is_active':True})


    return render(request, 'my_timer_main/main/client_edit.html', {'form': form})

@log_exception(None)
@login_required
def client_delete(request, client_id = ""):
    client = get_object_or_404(Clients, pk=client_id)
    client.delete()
    return HttpResponseRedirect(reverse('my_timer:client_list'))

@log_exception(None)
@login_required
def task_list(request):
    cache_key_filter = 'task_list_cache_filter'
    timeout_cache = None
    filter_list = ['task_name', 'only_active', 'client']
    type_of_filter = request.GET.get('search_button', "")
    if type_of_filter:
        if type_of_filter == 'clear_search':
            dic_of_filter = dict.fromkeys(filter_list)
        else:
            dic_of_filter = {key: request.GET.get(key, None) for key in filter_list}
        caches['mem_cache'].set(cache_key_filter, dic_of_filter, timeout=timeout_cache)
    else:
        dic_of_filter = caches['mem_cache'].get(cache_key_filter, None)
        if dic_of_filter is None:
            dic_of_filter = dict.fromkeys(filter_list)
            caches['mem_cache'].set(cache_key_filter, dic_of_filter, timeout=timeout_cache)


    array_list_of_q = []
    for key, value in dic_of_filter.items():
        if value and value is not None:
            if key == "only_active" and dic_of_filter[key]:
                dic_of_filter[key] = value == "on"
                # array_list_of_q.append(Q(date_stop__gte=dic_of_filter[key].astimezone(pytz.UTC)))
                array_list_of_q.append(Q(is_active=dic_of_filter[key]))
            elif key == "task_name":
                array_list_of_q.append(Q(name__icontains=value))
            elif key == "client" and dic_of_filter[key]:
                dic_of_filter[key] = get_object_or_404(Clients, pk=value)
                array_list_of_q.append(Q(client__name__icontains=dic_of_filter[key]))
                # dic_of_filter[key] = Clients.id
    q = None
    if len(array_list_of_q):
        for q_ in array_list_of_q:
            if q is None:
                q = q_
            else:
                q = q_ & q
    if q is not None:
        tasks = Tasks.objects.select_related().filter(q).all()
    else:
        tasks = Tasks.objects.select_related().all()

    paginator = Paginator(tasks, Pref.get_pref_by_name('task_count_item_on_page', 10))
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)

    initial_dic = {key: value for (key, value) in dic_of_filter.items() if value and value is not None}
    form_search = FormTasksFilter(initial=initial_dic)    
    context = {'tasks': page.object_list, 'form_search':form_search, 'page':page}
    return render(request, 'my_timer_main/main/task_list.html', context)

# @log_exception(None)
# @login_required
# def task_edit_or_add(request, task_id = "", comment_id= ""):
#     task = None
#     if task_id:
#         task = get_object_or_404(Tasks, pk=task_id)
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         if task:
#             form = FormChangeTask(request.POST, instance=task)
#         else:
#             form = FormChangeTask(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required
#             # ...
#             # redirect to a new URL:
#             form.save(commit=True)
#             return HttpResponseRedirect(reverse('my_timer:task_list'))

#     # if a GET (or any other method) we'll create a blank form
#     else:
#         if task:
#             form = FormChangeTask(initial={'user': request.user.pk, 'is_active':True}, instance=task)
#         else:
#             form = FormChangeTask(initial={'user': request.user.pk, 'is_active':True})


#     return render(request, 'my_timer_main/main/task_edit.html', {'form': form})

class TaskEdit(LoginRequiredMixin, ProcessFormView, TemplateResponseMixin):
    class_task = FormChangeTask
    class_comment = FormCommentEdit
    dic_of_form = {}
    template_name = "my_timer_main/main/task_edit.html"
    url_save_and_close = reverse_lazy('my_timer:task_list')
    user = None
    curr_task = None
    curr_comment = None
    curr_form = None
    success_url = None
    # def get_form_class(self):
    #     pass

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     if hasattr(self, 'object'):
    #         kwargs.update({'instance': self.object})
    #     kwargs.update({"initial":{'user': self.user.pk, 'is_active':True}})
    #     return kwargs

    # def get_success_url(self):
    #     if 'save_and_close' in self.request.POST:
    #         return self.url_save_and_close
    #     else:
    #         return reverse('my_timer:task_edit', kwargs={'task_id': self.object.id})
    def collect_info_from_request(self, **kwargs):
        self.curr_task = None
        self.curr_comment = None
        if kwargs.get("task_id", None) is not None:
            self.curr_task = get_object_or_404(Tasks, pk=kwargs.get("task_id"))
        if kwargs.get("comment_id", None) is not None:
            self.curr_comment = get_object_or_404(Comments, pk=kwargs.get("comment_id"))


    def inialize_form(self, **kwargs):
        if self.curr_task is not None:
            kwargs["instance"] = self.curr_task
        self.dic_of_form["form_task_edit"] = self.class_task(**kwargs)
        kwargs.pop("instance", None)
        if self.curr_comment is not None:
            kwargs["instance"] = self.curr_comment
        self.dic_of_form["form_comment_edit"] = self.class_comment(**kwargs)

    def post_collect_param(self):
        if 'comment_save_and_close' in self.request.POST:
            self.curr_form = self.dic_of_form["form_comment_edit"]
            self.success_url = self.url_save_and_close
        elif 'task_save_and_close' in self.request.POST:
            self.curr_form = self.dic_of_form["form_task_edit"]
            self.success_url = self.url_save_and_close
        elif 'comment_save' in self.request.POST:
            self.curr_form = self.dic_of_form["form_comment_edit"]
            self.success_url = reverse('my_timer:task_edit', kwargs={'task_id': self.curr_task.id})
        elif 'task_save' in self.request.POST:
            self.curr_form = self.dic_of_form["form_task_edit"]
            self.success_url = reverse('my_timer:task_edit', kwargs={'task_id': self.curr_task.id})
    
    def get_form(self):
        return self.curr_form
    
    def get_context_data(self):
        data = {'form_task_edit': self.dic_of_form["form_task_edit"],'form_comment_edit': self.dic_of_form["form_comment_edit"]}
        # data = {'form_task_edit': FormChangeTask(initial={'user': 1, 'is_active':True}, instance=self.curr_task)}
        comment_query = Comments.objects.filter(user=self.user, task=self.curr_task).order_by('-update_at').all()
        data['not_has_comment_edit'] = self.curr_comment is None
        data['array_of_comment'] = [{'content': comment.content, 
                'edit': (self.curr_comment is not None and comment.id == self.curr_comment.id),
                'update_at':comment.update_at,
                'task_id': comment.task.id,
                'comment_id': comment.id} for comment in comment_query]

        return data

    def post(self, request, *args, **kwargs):
        self.user = request.user
        self.collect_info_from_request(**kwargs)
        self.inialize_form(data=self.request.POST)
        self.post_collect_param()
        return super().post(self, request, *args, **kwargs)

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        pass

    def get(self, request, *args, **kwargs):
        self.user = request.user
        self.collect_info_from_request(**kwargs)
        self.inialize_form(initial={'user': request.user.pk, 'is_active':True, 'task':self.curr_task})
        return super().get(self, request, *args, **kwargs)


class TaskNew(LoginRequiredMixin, CreateView):
    template_name = "my_timer_main/main/task_add.html"
    url_save_and_close = reverse_lazy('my_timer:task_list')
    model = Task
    form_class = FormChangeTask
    user = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({"initial":{'user': self.user.pk, 'is_active':True}})
        return kwargs

    def get_success_url(self):
        if 'save_and_close' in self.request.POST:
            return self.url_save_and_close
        else:
            return reverse('my_timer:task_edit', kwargs={'task_id': self.object.id})

    def post(self, request, *args, **kwargs):
        self.user = request.user
        return super().post(self, request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        self.user = request.user
        return super().get(self, request, *args, **kwargs)

@log_exception(None)
@login_required
def task_delete(request, task_id):
    # try:
    task = get_object_or_404(Tasks, pk=task_id)
    task.delete()
    # except:
    #     pass
    return HttpResponseRedirect(reverse('my_timer:task_list'))

@log_exception(None)
@login_required
def work_place(request):
    # last_tasks = Tasks.objects.
    def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def get_last_task(count_last_tasks:int, clien_filter_id:int, task_name:str, user:User, date_now:dt):
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
            date_start_plan
            is_plan - это задача с датой начала
            is_outdate - это задача уже просрочена
        """
        # task_name = "test"
        # clien_filter_id = 1
        query_task = Tasks.objects.filter(user=user).filter(is_active=True).filter(is_delete=False)
        if task_name:
            query_task = query_task.filter(name__icontains=task_name)
        if clien_filter_id:
            query_task = query_task.filter(client__id=clien_filter_id)
        query_task = query_task.values("pk")

        # time_track_duration_after_plan = TimeTrack.objects.filter(task__date_start_plan__lte=date_now).filter(date_stop__gte=F('task__date_start_plan'))
        #             .annotate()

        time_track_query = TimeTrack.objects.filter(task__id__in=query_task).filter(is_delete=False).filter(user=user).values("task__id").order_by().annotate(date_max=Max("date_stop"),
                duration=Sum("duration_sec"),is_plan=Value(0), 
                duration_after_plan=Sum("duration_sec", filter=(Q(task__date_start_plan__lte=date_now)&
                Q(date_stop__gte=F('task__date_start_plan'))))).values("task_id",
                 "date_max", "duration", "is_plan", "duration_after_plan")
        
        time_track_id_exist = TimeTrack.objects.filter(is_delete=False).values("task__id").distinct()

        qery_task_plan = Tasks.objects.filter(is_active=True,user=user, date_start_plan__lte=date_now, id__in=query_task).exclude(id__in=time_track_id_exist).filter(is_delete=False).annotate(task_id=F('id'), 
                date_max=F('date_start_plan'), duration=Value(0), is_plan=Value(1), duration_after_plan=Value(0)).values("task_id", "date_max", "duration", "is_plan", "duration_after_plan")
        
        union_query = time_track_query.union(qery_task_plan).order_by("-is_plan", "-date_max")[:count_last_tasks]
        # т.к. join не поддерживается django orm, будем просто получать доп данные, вторым запросом.
        list_of_id = [elem.get("task_id") for elem in union_query]
        addition_info = Tasks.objects.filter(id__in=list_of_id).filter(is_delete=False).select_related("client").all()
        dic_addit_info = {}
        for elem in addition_info:
            dic_addit_info[elem.id] = elem
        array_of_result = []
        tz_curr = get_current_timezone()
        for elem in union_query:
            dic_of_data = {}
            temp_task = dic_addit_info.get(elem.get("task_id"))
            dic_of_data["task_id"] = elem.get("task_id")
            dic_of_data["max_date"] = None if elem.get("is_plan") == 1 else elem.get("date_max")
            dic_of_data["task_name"] = temp_task.name
            dic_of_data["task_is_acitve"] = temp_task.is_active
            dic_of_data["client_name"] = temp_task.client.name
            dic_of_data["client_id"] = temp_task.client.id
            dic_of_data["task_duration"] = elem.get("duration")
            dic_of_data["date_start_plan"] = temp_task.date_start_plan
            dic_of_data['diff_day'] = 0
            dic_of_data['is_plan'] = False
            dic_of_data['is_outdate'] = False
            if temp_task.date_start_plan is not None and (elem["duration_after_plan"] is None or elem["duration_after_plan"] < 100):
                dic_of_data['is_plan'] = True
                if dic_of_data["date_start_plan"] < datetime.date.today():
                    dic_of_data['is_outdate'] = True

            if elem['date_max'] is not None:
                max_date = elem['date_max']
                max_date = max_date.replace(tzinfo=tz_curr)
                if max_date:
                    dic_of_data['diff_day'] = (tz.now().date() - max_date.date()).days
            array_of_result.append(dic_of_data)
        array_of_result.sort(key=lambda elem:(not elem['is_plan'], elem['diff_day']))
        # if not clien_filter_id:
        #     clien_filter_id = None
        # dic_of_data = {}
        # tz_curr = get_current_timezone()
        # with connection.cursor() as cursor:
        #     # cursor.execute("""SELECT last_tasks.task_id as task_id, last_tasks.duration as task_duration, last_tasks.max_date as max_date, main_tasks.name as task_name, 
        #     # main_tasks.is_active as task_is_acitve, main_clients.name as client_name,  main_clients.id as client_id FROM
        #     #         (SELECT task_id, max(date_stop) as max_date, SUM(duration_sec) as duration from main_timetrack group BY task_id) as last_tasks LEFT JOIN
        #     #         main_tasks on last_tasks.task_id = main_tasks.id LEFT JOIN main_clients on main_tasks.client_id = main_clients.id
        #     #         WHERE main_tasks.is_active = 1 ORDER BY max_date DESC limit %s""", [count_last_tasks])
        #     cursor.execute("""SELECT last_tasks.task_id as task_id, last_tasks.duration as task_duration, last_tasks.max_date as max_date, main_tasks.name as task_name, 
        #     main_tasks.is_active as task_is_acitve, main_clients.name as client_name,  main_clients.id as client_id FROM
        #             (SELECT task_id, max(date_stop) as max_date, SUM(duration_sec) as duration from main_timetrack WHERE 
        #             (task_id in (SELECT id  from main_tasks WHERE (LOWER(main_tasks.name) like LOWER(%(like_name)s) or %(like_name)s IS NULL) and (main_tasks.client_id in (SELECT id FROM main_clients WHERE (id = %(clien_id)s OR %(clien_id)s IS NULL))) )) group BY task_id) as last_tasks LEFT JOIN
        #             main_tasks on last_tasks.task_id = main_tasks.id LEFT JOIN main_clients on main_tasks.client_id = main_clients.id
        #             WHERE main_tasks.is_active = TRUE ORDER BY max_date DESC limit %(count_elem)s""", {'like_name': f'%{task_name}%' if task_name else None, 'clien_id': clien_filter_id, 'count_elem':count_last_tasks})
        #     dic_of_data = dictfetchall(cursor)
        #     # разницу рассчитаем вручную, т.к.в разных типах БД разные функции
        #     for elem in dic_of_data:
        #         elem['diff_day'] = ''
        #         if elem['max_date'] is not None:
        #             # max_date = parse_datetime(elem['max_date'])
        #             # max_date = max_date.replace(tzinfo=tz_curr)
        #             max_date = elem['max_date']
        #             max_date = max_date.replace(tzinfo=tz_curr)
        #             if max_date:
        #                 elem['diff_day'] = (tz.now().date() - max_date.date()).days
                
        return array_of_result
    
    message = ""
    cache_key_filter = 'work_place_cache_filter'
    timeout_cache = None
    filter_list = ['task_name', 'client']
    type_of_filter = request.GET.get('search_button', "")
    if type_of_filter:
        if type_of_filter == 'clear_search':
            dic_of_filter = dict.fromkeys(filter_list)
        else:
            dic_of_filter = {key: request.GET.get(key, None) for key in filter_list}
            if dic_of_filter['client']:
                dic_of_filter['client'] = get_object_or_404(Clients, pk=dic_of_filter['client'])
            
        caches['mem_cache'].set(cache_key_filter, dic_of_filter, timeout=timeout_cache)
    else:
        dic_of_filter = caches['mem_cache'].get(cache_key_filter, None)
        if dic_of_filter is None:
            dic_of_filter = dict.fromkeys(filter_list)
            caches['mem_cache'].set(cache_key_filter, dic_of_filter, timeout=timeout_cache)
    



    if request.method == 'POST' and request.POST.get('task') is not None:
        task_to_start = None
        task_name = request.POST.get('task')
        client_id = request.POST.get('client')
        client = Clients.objects.get(pk = client_id)
        task = Tasks.objects.filter(name__icontains=task_name, client=client).all()
        if task.count() == 1:
            task_to_start = task[0]
        elif task.count() > 1:
            message = "По данному клиенту уже есть такая задача, запустите ее из списка задач"
        else:
            task_to_start = Tasks(name=task_name, client=client, is_active=True, user=request.user)
            task_to_start.save()
        
        if task_to_start is not None:
            action_wich_tasks(request=request, action="start", id=task_to_start.pk)

    array_dic_of_data_last_tasks = get_last_task(Pref.get_pref_by_name('work_place_count_last_task', 10), dic_of_filter['client'].id if dic_of_filter['client'] else None,
            dic_of_filter['task_name'], request.user, date_now=dt.today())
    active_time_treket = TimeTrack.objects.select_related().filter(is_active = True).order_by('-date_start')

    # keyword  = ''
    # form_search = SearchForm(initial={'keyword': keyword})
    form_new_task = FormNewTask()

    initial_dic = {key: value for (key, value) in dic_of_filter.items() if value and value is not None}
    form_search = FormWokrPlaceFilter(initial=initial_dic)
    # form_test = FormTestWidget()
    list_last_time_track = TimeTrack.objects.filter(user=request.user).order_by("-date_stop")[:4]
    context = {'array_dic_of_data_last_tasks': array_dic_of_data_last_tasks,'active_time_treket':active_time_treket,
            'form_new_task':form_new_task, 'form_search': form_search, "list_last_time_track":list_last_time_track,}
    return render(request, 'my_timer_main/main/work_place.html', context)


# def get_five_ico(request):
#     result = finders.find('main/favicon.ico')
#     searched_locations = finders.searched_locations
#     image_data = open(searched_locations, "rb").read()
#     return HttpResponse(image_data, mimetype="image/png")   

@log_exception(None)
@login_required
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
        count_active_task_add()
    elif action == "stop":
        time_track = get_object_or_404(TimeTrack, pk=id)
        time_track.date_stop = tz.now()
        time_track.save()
        count_active_task_minus()
    elif action == "task_done":
        task = get_object_or_404(Tasks, pk=id)
        task.is_active = False
        task.save()
    else:
        return HttpResponse(f'action "{action}" not possible')

    
    return HttpResponseRedirect(reverse('my_timer:work_place'))

@log_exception(None)
@login_required
def report_task_list(request):
    return render(request, 'my_timer_main/main/report_tasks_clients.html')

# def cleint_filter(request, filter_text):

#     # request.session.
#     request.session['client_filter'] = filter_text
#     return HttpResponseRedirect(reverse('my_timer:client_list'))

@log_exception(None)
@login_required
def time_track_list(request):
    cache_key_filter = 'time_track_list_cache_filter'
    timeout_cache = None
    filter_list = ['date_from', 'date_to', 'task_name', 'client']
    type_of_filter = request.GET.get('search_button', "")
    if type_of_filter:
        if type_of_filter == 'clear_search':
            dic_of_filter = dict.fromkeys(filter_list)
        else:
            dic_of_filter = {key: request.GET.get(key, None) for key in filter_list}
        caches['mem_cache'].set(cache_key_filter, dic_of_filter, timeout=timeout_cache)
    else:
        dic_of_filter = caches['mem_cache'].get(cache_key_filter, None)
        if dic_of_filter is None:
            dic_of_filter = dict.fromkeys(filter_list)
            caches['mem_cache'].set(cache_key_filter, dic_of_filter, timeout=timeout_cache)


    array_list_of_q = []
    for key, value in dic_of_filter.items():
        if value is not None:
            if key == "date_from" and dic_of_filter[key]:
                dic_of_filter[key] = date_convert_from_string(value)
                # array_list_of_q.append(Q(date_stop__gte=dic_of_filter[key].astimezone(pytz.UTC)))
                array_list_of_q.append(Q(date_stop__gte=dic_of_filter[key]))
            elif key == "date_to" and dic_of_filter[key]:
                dic_of_filter[key] = date_end_of_day(date_convert_from_string(value))
                array_list_of_q.append(Q(date_stop__lte=dic_of_filter[key]))
            elif key == "task_name":
                array_list_of_q.append(Q(task__name__icontains=value))
            elif key == "client" and dic_of_filter[key]:
                dic_of_filter[key] = get_object_or_404(Clients, pk=value)
                array_list_of_q.append(Q(task__client=dic_of_filter[key]))
                # dic_of_filter[key] = Clients.id
    q = None
    if len(array_list_of_q):
        for q_ in array_list_of_q:
            if q is None:
                q = q_
            else:
                q = q_ & q
    if q is not None:
        time_trackers = TimeTrack.objects.select_related().filter(q).all()
    else:
        time_trackers = TimeTrack.objects.select_related().all()

    initial_dic = {key: value for (key, value) in dic_of_filter.items() if value and value is not None}
    form_search = FormTameTrackerFilter(initial=initial_dic)
    # if initial_dic.get('client'):
    #     form_search.fields['client'].choices = Clients.objects.get(pk=2)
    context = {'time_trackers': time_trackers, 'form_search':form_search, }
    return render(request, 'my_timer_main/main/time_track_list.html', context)

@log_exception(None)
@login_required
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

@log_exception(None)
@login_required
def time_track_delete(request, time_track_id):
    # TimeTrack.objects.filter(id=time_track_id).delete()
    TimeTrackObject = get_object_or_404(TimeTrack, pk=time_track_id)
    TimeTrackObject.delete()
    return HttpResponseRedirect(reverse('my_timer:time_track_list'))

@log_exception(None)
@login_required
def comment_delete(request, task_id, comment_id):
    # TimeTrack.objects.filter(id=time_track_id).delete()
    CommentObject = get_object_or_404(Comments, pk=comment_id)
    CommentObject.delete()
    return HttpResponseRedirect(reverse('my_timer:task_edit', kwargs={'task_id': task_id}))

