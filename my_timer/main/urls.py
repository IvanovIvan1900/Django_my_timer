from django.urls import path, re_path
from .views import client_list
from django.conf import settings 
from django.views.decorators.cache import never_cache
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve 
from .views import client_edit_or_add, client_delete
# from .views import cleint_filter
from . import views
from .views import task_list, task_edit_or_add, task_delete
from .views import work_place
from .views import action_wich_tasks
from .views import time_track_list, time_track_edit_or_add


app_name = "my_timer"

urlpatterns = [
    path('', views.client_list, name='index'),
    # path(r'^user\/(?P<username>\w{0,50})', cleint_filter, name = 'cleint_filter'),
    # path('cleint_filter/<str:filter_text>/', cleint_filter, name = 'cleint_filter'),
    path('client_edit/<int:client_id>/', client_edit_or_add, name = 'client_edit'),
    path('client_delete/<int:client_id>/', client_delete, name = 'client_delete'),
    path('client_add/', client_edit_or_add, name = 'client_add'),
    path('client_list/', client_list, name = 'client_list'),
    path('task_edit/<int:task_id>/', task_edit_or_add, name = 'task_edit'),
    path('task_delete/<int:task_id>/', task_delete, name = 'task_delete'),
    path('task_add/', task_edit_or_add, name = 'task_add'),
    path('task_list/', task_list, name = 'task_list'),
    path('work_place/', work_place, name = 'work_place'),
    path('time_track_list/', time_track_list, name = 'time_track_list'),
    path('time_track_edit/<int:time_track_id>/', time_track_edit_or_add, name = 'time_track_edit'),
    path('time_track_add/', time_track_edit_or_add, name = 'time_track_add'),
    path('action_wich_taks/<str:action>/<int:id>', action_wich_tasks, name = 'action_wich_tasks'),
]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 