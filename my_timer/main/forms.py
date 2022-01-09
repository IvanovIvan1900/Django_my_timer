from django.db import models
from django.db.models import fields
from .models import Clients
from django import forms
from .models import Tasks
from .models import TimeTrack
from django_select2 import forms as s2forms
from .utility import get_qery_client_wich_cahce, get_qery_active_task_wich_cahce
from tempus_dominus.widgets import DatePicker

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
    class Meta:
        model = Tasks
        fields = ['name', 'client', 'is_active', 'user', 'description']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

class FormNewTask(forms.Form):
    task = forms.CharField(required=True, max_length=100, label='Задача')
    # client = forms.ModelChoiceField(queryset= Clients.objects.all(), required=True, label='Клиент')
    client = forms.ChoiceField(widget=ClientWidget(), required=True, label='Клиент')

class FromChangeTimeTracker(forms.ModelForm):
    class Meta:
        model = TimeTrack
        fields = ['task', 'date_start', 'date_stop', 'duration_sec', 'is_active', 'user']
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput}

class FormTameTrackerFilter(forms.Form):
    date_from = forms.DateField(widget=DAV_DataFieldWidget(), label="C", required= False)
    date_to = forms.DateField(widget=DAV_DataFieldWidget(), label="По", required= False)
    task_name = forms.CharField(max_length=100, label='Задача', required= False)
    client = forms.ChoiceField(widget=ClientWidget(), label='Клиент', required= False)

# class ClientWidget(s2forms.ModelSelect2Widget):
#     search_fields = [
#         "name__icontains",
#         "full_name_icontains",
#     ]

    # def get_queryset(self):
    #     # original qs
    #     qs = super().get_queryset()
    #     return qs.filter(name__startswith=self.kwargs['name'])
# class TaskWidget(s2forms.Select2Mixin):
#     search_fields = [
#         "name__icontains",
#     ]
#     model = Tasks
#     empty_label = "-- выберите Задачу --"
#     cache_qery_key = "task_cache_query"

#     def __init__(self, **kwargs):
#         super().__init__(kwargs)
#         self.attrs = {"style": "min-width: 250px" }
#         # self.empty_label = 'Не выбран'

#     def build_attrs(self, base_attrs, extra_attrs=None):
#         base_attrs = super().build_attrs(base_attrs, extra_attrs)
#         base_attrs.update(
#             {"data-minimum-input-length": 0, "data-placeholder": self.empty_label, 'data-allow-clear':'true'}
#         )
#         return base_attrs

#     def get_queryset(self):
#         return get_qery_active_task_wich_cahce(Tasks)
# class TaskWidget(s2forms.Select2Widget):
#     search_fields = [
#         "name__icontains",
#     ]
#     model = Tasks
#     empty_label = "-- выберите Задачу --"
#     cache_qery_key = "task_cache_query"

#     def __init__(self, **kwargs):
#         super().__init__(kwargs)
#         self.attrs = {"style": "min-width: 250px" }
#         # self.empty_label = 'Не выбран'

#     def build_attrs(self, base_attrs, extra_attrs=None):
#         base_attrs = super().build_attrs(base_attrs, extra_attrs)
#         base_attrs.update(
#             {"data-minimum-input-length": 0, "data-placeholder": self.empty_label, 'data-allow-clear':'true'}
#         )
#         return base_attrs

#     def get_queryset(self):
#         return get_qery_active_task_wich_cahce(Tasks)

class FormTestWidget(forms.Form):
    # list_of_client = ((client.id, client.name) for client in  Clients.objects.all())
    # task = forms.CharField(max_length=250, widget=TaskWidget())
    #https://pypi.org/project/django-tempus-dominus/
    date_field = forms.DateField(widget=DAV_DataFieldWidget())
    client = forms.ChoiceField(widget=ClientWidget())