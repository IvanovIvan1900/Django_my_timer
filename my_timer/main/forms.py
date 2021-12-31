from django.db.models import fields
from .models import Clients
from django import forms

class FormChangeClient(forms.ModelForm):
    class Meta:
        model = Clients
        # fields = ['name', 'full_name', 'is_active']
        exclude = ['user']
        widgets = {'user': forms.HiddenInput}