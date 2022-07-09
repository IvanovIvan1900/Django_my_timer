from django.conf import settings
from django.contrib.staticfiles.views import serve
from django.urls import path
from django.views.decorators.cache import never_cache

from .views import (ClientList, TimeTrackReport, TimeTreckerDetalView,
                    TimeTreckerList, get_report_html, get_report_pdf,
                    set_account_date)

urlpatterns = [
    path('tt/<int:pk>/', TimeTreckerDetalView),
    path('tt/', TimeTreckerList),
    path('clients/', ClientList),
    path('reports/time_track/', TimeTrackReport, name = "time_track_report"),
    path('reports/pdf_report/', get_report_pdf),
    path('reports/html_report/', get_report_html),
    path('reports/set_date_account/', set_account_date),
]

# if settings.DEBUG:
#     urlpatterns.append(path('static/<path:path>', never_cache(serve)))
