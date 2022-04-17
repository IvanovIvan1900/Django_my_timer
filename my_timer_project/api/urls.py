from .views import ClientList, TimeTreckerList, TimeTreckerDetalView, TimeTrackReport
from django.urls import path

urlpatterns = [
    path('tt/<int:pk>/', TimeTreckerDetalView),
    path('tt/', TimeTreckerList),
    path('clients/', ClientList),
    path('reports/time_track/', TimeTrackReport),
]