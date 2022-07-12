import datetime

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import fields
from pkg_resources import require
from main.widgets import (ClientWidget, DAV_DataFieldWidget, DAV_DateTimePicker)

from .models import Clients, Comments, Tasks, TimeTrack
from .utility import (get_qery_active_task_wich_cahce,
                      get_qery_client_wich_cahce)
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class FormChangeClient(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ['name', 'full_name', 'is_active', 'user']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=30, label='')

class FormTasksFilter(forms.Form):
    task_name = forms.CharField(max_length=100, label='Задача', required= False, widget=forms.TextInput(attrs={'style':'width:500px'}))
    client = forms.ModelChoiceField(queryset=get_qery_client_wich_cahce(Clients), widget=ClientWidget(), label='Клиент', required= False)
    only_active = forms.BooleanField(label="Активные", required=False)

class FormChangeTask(forms.ModelForm):
    date_start_plan = forms.DateField(required=False,
         label='Дата начала (План)', widget=DAV_DataFieldWidget(), input_formats=("%d.%m.%Y",))
    client = forms.ModelChoiceField(queryset=get_qery_client_wich_cahce(Clients), widget=ClientWidget(attrs={'id':'add_task_customer'}),
         label='Клиент', required= True)

    class Meta:
        model = Tasks
        fields = ['name', 'client', 'is_active', 'user', 'description', 'date_start_plan']
        labels = {'name': 'Наименование', 'is_active':'Активна', 'description':'Описание'}
        widgets = {'user': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super(FormChangeTask, self).__init__(*args, **kwargs)
        self.fields['description'].required = False

    def clean(self):
        super().clean()
        errors = {}
        if self.data["date_start_plan"]:
            try:
                date_start_plan = datetime.datetime.strptime(self.data["date_start_plan"], "%d.%m.%Y").date()
                self.cleaned_data["date_start_plan"] = date_start_plan
            except ValueError as e:
                errors["date_start_plan"] = ValidationError(
                            'Укажите дату в корректном формате. Ожидается ДД.ММ.ГГГГ')
        if errors:
            raise ValidationError(errors)

class FormNewTask(forms.Form):
    task = forms.CharField(required=True, max_length=100, label='Задача')
    # client = forms.ModelChoiceField(queryset= Clients.objects.all(), required=True, label='Клиент')
    client = forms.ModelChoiceField(queryset=get_qery_client_wich_cahce(Clients), widget=ClientWidget(attrs={'id':'add_task_customer'}), label='Клиент', required= True)
    # client = forms.ChoiceField(widget=ClientWidget(), required=True, label='Клиент')

class FromChangeTimeTracker(forms.ModelForm):
    date_start= forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M'], 
        widget=DAV_DateTimePicker(format='%d.%m.%Y %H:%M'),
        label='Дата начала'

    )
    date_stop= forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M'], 
        widget=DAV_DateTimePicker(format='%d.%m.%Y %H:%M'),
        label='Дата окончания'
    )

    date_account = forms.DateField(
        input_formats=('%d.%m.%Y',), 
        required= False,
        widget=DAV_DataFieldWidget(),
        label='Дата счета'

    )

    duration_sec = forms.CharField(label='Продолжительность', required = False)
    class Meta:
        model = TimeTrack
        fields = ['task', 'date_start', 'date_stop', 'duration_sec', 'is_active', 'user', 'date_account']
        labels = {'task': 'Задача', 'duration_sec':'Продолжительность', 'is_active':'Задача активна'}
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

    def clean_duration_sec(self):
        return (self.cleaned_data['date_stop'] - self.cleaned_data['date_start']).total_seconds()
        
class FormTameTrackerFilter(forms.Form):
    date_from = forms.DateField(widget=DAV_DataFieldWidget(), label="C", required= False)
    date_to = forms.DateField(widget=DAV_DataFieldWidget(), label="По", required= False)
    task_name = forms.CharField(max_length=100, label='Задача', required= False, widget=forms.TextInput(attrs={'style':'width:500px'}))
    client = forms.ModelChoiceField(queryset=get_qery_client_wich_cahce(Clients), widget=ClientWidget(), label='Клиент', required= False)
    # client = forms.ModelChoiceField(queryset=Clients.objects.all(), label='Клиент', required= False)

class FormWokrPlaceFilter(forms.Form):
    # date_from = forms.DateField(widget=DAV_DataFieldWidget(), label="C", required= False)
    # date_to = forms.DateField(widget=DAV_DataFieldWidget(), label="По", required= False)
    task_name = forms.CharField(max_length=100, label='Задача', required= False, widget=forms.TextInput(attrs={'style':'width:500px'}))
    client = forms.ModelChoiceField(queryset=get_qery_client_wich_cahce(Clients), widget=ClientWidget(attrs={'id':'filter_customer'}), label='Клиент', required= False, )

class FormTestWidget(forms.Form):
    # list_of_client = ((client.id, client.name) for client in  Clients.objects.all())
    # task = forms.CharField(max_length=250, widget=TaskWidget())
    #https://pypi.org/project/django-tempus-dominus/
    date_field = forms.DateField(widget=DAV_DataFieldWidget())
    client = forms.ChoiceField(widget=ClientWidget())

class FormCommentEdit(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ['task', 'content',  'user']
        labels = {'task': 'Задача', 'content':''}
        widgets = {'user': forms.HiddenInput, 'task': forms.HiddenInput, 'content':CKEditorUploadingWidget(), 'update_at':forms.HiddenInput}
