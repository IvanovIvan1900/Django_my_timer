from django.urls import path, re_path, include
from .views import client_list, report_task_list
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
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView

app_name = "my_timer"

urlpatterns = [
    path('', LoginView.as_view(), name='index'),
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
    path('report_task_list/', report_task_list, name = 'report_task_list'),
    # re_path(r'^time_track_list_filter(?:/(<task_name>\w*))?(?:/(<client>\w*))?(?:/(<search_button>\w*))?/$', time_track_list, name = 'time_track_list_filter'),
    re_path(r'^time_track_list_filter/$', time_track_list, name = 'time_track_list_filter'),
    path('time_track_list/', time_track_list, name = 'time_track_list'),
    path('time_track_edit/<int:time_track_id>/', time_track_edit_or_add, name = 'time_track_edit'),
    path('time_track_add/', time_track_edit_or_add, name = 'time_track_add'),
    path('action_wich_taks/<str:action>/<int:id>', action_wich_tasks, name = 'action_wich_tasks'),
    # path(r'^select2/', include('select2.urls')),
    path("select2/", include("django_select2.urls")),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='my_timer:login'), name='logout'),
    path('accounts/password/change/', PasswordChangeView.as_view(template_name='registration/change_password.html'),
        name='password_change'),

]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 