from django.urls import path
from .views import client_list
from django.conf import settings 
from django.views.decorators.cache import never_cache
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve 
from .views import client_edit_or_add
from .views import client_delete
# from .views import cleint_filter
from . import views

app_name = "my_timer"

urlpatterns = [
    path('', views.client_list, name='index'),
    # path(r'^user\/(?P<username>\w{0,50})', cleint_filter, name = 'cleint_filter'),
    # path('cleint_filter/<str:filter_text>/', cleint_filter, name = 'cleint_filter'),
    path('client_edit/<int:client_id>/', client_edit_or_add, name = 'client_edit'),
    path('client_delete/<int:client_id>/', client_delete, name = 'client_delete'),
    path('client_add/', client_edit_or_add, name = 'client_add'),
    path('client_list/', client_list, name = 'client_list'),
]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 