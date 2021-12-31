from django.contrib import admin
from .models import Clients

# Register your models here.
@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', "is_active")
    