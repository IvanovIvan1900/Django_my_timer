from django.contrib import admin
from .models import Clients, Comments
from .models import Tasks
from .models import TimeTrack
# from datetime import datetime as dt
from django.utils import timezone as tz

# Register your models here.
@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', "is_active", "is_delete")
    
@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', "is_active", "is_delete")

@admin.register(TimeTrack)
class TrakAdmin(admin.ModelAdmin):
    list_display = ('task', 'date_start', 'date_stop','duration_sec', "is_delete")
    def get_changeform_initial_data(self, request):
        return {'date_start': tz.now()}

@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'content', 'user', "is_delete")
    readonly_fields=('update_at',)
    def get_changeform_initial_data(self, request):
        return {'update_at': tz.now()}

