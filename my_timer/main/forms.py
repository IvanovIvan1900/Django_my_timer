from django.db import models
from django.db.models import fields
from .models import Clients
from django import forms
from .models import Tasks
from .models import TimeTrack

class FormChangeClient(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ['name', 'full_name', 'is_active', 'user']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=30, label='')

class FormChangeTask(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = ['name', 'client', 'is_active', 'user', 'description']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

class FormNewTask(forms.Form):
    task = forms.CharField(required=True, max_length=100, label='Наименование задачи')
    client = forms.ModelChoiceField(queryset= Clients.objects.all(), required=True, label='Клиент')

class FromChangeTimeTracker(forms.ModelForm):
    class Meta:
        model = TimeTrack
        fields = ['task', 'date_start', 'date_stop', 'duration_sec', 'is_active', 'user']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}
