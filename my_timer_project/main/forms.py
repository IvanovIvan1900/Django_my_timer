import datetime
from django.conf import settings
from django.db import models
from django.db.models import fields
from .models import Clients
from django import forms
from .models import Tasks
from .models import TimeTrack
from django_select2 import forms as s2forms
from .utility import get_qery_client_wich_cahce, get_qery_active_task_wich_cahce
from tempus_dominus.widgets import DatePicker
from django.core.exceptions import ValidationError

#=================================================
#+++++++++++++MY WIDHET++++++++++++++++++++++++++
class ClientWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "full_name__icontains",
    ]
    model = Clients
    empty_label = "-- выберите клиента --"
    cache_qery_key = "client_cache_query"

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {"style": "min-width: 250px" }
        if kwargs.get('attrs', {}).get('id', None):
            self.attrs['id'] = kwargs.get('attrs', {}).get('id', None)
        # self.empty_label = 'Не выбран'

    def build_attrs(self, base_attrs, extra_attrs=None):
        base_attrs = super().build_attrs(base_attrs, extra_attrs)
        base_attrs.update(
            {"data-minimum-input-length": 0, "data-placeholder": self.empty_label, 'data-allow-clear':'true'}
        )
        return base_attrs

    def get_queryset(self):
        return get_qery_client_wich_cahce(Clients)

class DAV_DataFieldWidget(DatePicker):
    dav_options={'buttons':{'showToday':True, 'showClear':True, 'showClose':True}}
    def __init__(self, attrs=None, options=None, format=None):
        if isinstance(options , dict):
            options = {**options, **self.dav_options}
        else:
            options = self.dav_options
        super().__init__(attrs=attrs, options=options, format=format)

#-------------MY WIDHET--------------------------
#=================================================

class FormChangeClient(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ['name', 'full_name', 'is_active', 'user']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=30, label='')

class FormChangeTask(forms.ModelForm):
    date_start_plan = forms.DateField(required=False,
         label='Дата начала (План)', widget=DAV_DataFieldWidget(), input_formats=("%d.%m.%Y",))
    class Meta:
        model = Tasks
        fields = ['name', 'client', 'is_active', 'user', 'description', 'date_start_plan']
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
    class Meta:
        model = TimeTrack
        fields = ['task', 'date_start', 'date_stop', 'duration_sec', 'is_active', 'user']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

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