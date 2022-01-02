from django.contrib import admin
from .models import Clients
from .models import Tasks

# Register your models here.
@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', "is_active")
    
@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', "is_active")
