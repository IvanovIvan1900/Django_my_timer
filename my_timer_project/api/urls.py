from django.conf import settings
from .views import ClientList, TimeTreckerList, TimeTreckerDetalView, TimeTrackReport, get_report_html, get_report_pdf
from django.urls import path
from django.views.decorators.cache import never_cache
from django.contrib.staticfiles.views import serve 

urlpatterns = [
    path('tt/<int:pk>/', TimeTreckerDetalView),
    path('tt/', TimeTreckerList),
    path('clients/', ClientList),
    path('reports/time_track/', TimeTrackReport),
    path('reports/pdf_report/', get_report_pdf),
    path('reports/html_report/', get_report_html),
]

# if settings.DEBUG:
#     urlpatterns.append(path('static/<path:path>', never_cache(serve)))
