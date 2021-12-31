from django.urls import path
from .views import client_list
from django.conf import settings 
from django.views.decorators.cache import never_cache
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve 
from .views import client_edit_or_add

app_name = "my_timer"

urlpatterns = [
    path('client_edit/<int:client_id>/', client_edit_or_add, name = 'client_edit'),
    path('client_add/', client_edit_or_add, name = 'client_add'),
    path('client_list/', client_list, name = 'client_list'),
]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 