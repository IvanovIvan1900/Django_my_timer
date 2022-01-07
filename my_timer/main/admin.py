from django.contrib import admin
from .models import Clients
from .models import Tasks
from .models import TimeTrack
# from datetime import datetime as dt
from django.utils import timezone as tz

# Register your models here.
@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', "is_active")
    
@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', "is_active")

@admin.register(TimeTrack)
class TrakAdmin(admin.ModelAdmin):
    list_display = ('task', 'date_start', 'date_stop','duration_sec')
    def get_changeform_initial_data(self, request):
        # a = dt.now()
        # tz_a = tz.now()
        return {'date_start': tz.now()}
