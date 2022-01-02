from django.db.models import fields
from .models import Clients
from django import forms
from .models import Tasks

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