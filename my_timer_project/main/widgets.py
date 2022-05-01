from django import forms
from django_select2 import forms as s2forms
from datetime import datetime
from main.utility import get_qery_client_wich_cahce
from tempus_dominus.widgets import DatePicker

from .models import Clients


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

    # class Media:
    #     css = {
    #         'all': ('https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.39.0/css/tempusdominus-bootstrap-4.min.css',),
    #     }
    #     js = ('//cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/moment-with-locales.min.js', '//cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.39.0/js/tempusdominus-bootstrap-4.min.js')


    def __init__(self, attrs=None, options=None, format=None):
        if isinstance(options , dict):
            options = {**options, **self.dav_options}
        else:
            options = self.dav_options
        super().__init__(attrs=attrs, options=options, format=format)

class DAV_DateTimePicker(forms.DateTimeInput):
    template_name = 'widgets/dav_datetimepicker.html'

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css',),
        }
        js = ('https://cdn.jsdelivr.net/jquery/latest/jquery.min.js', 'https://cdn.jsdelivr.net/momentjs/latest/moment-with-locales.min.js',
            'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js')

    # def get_context(self, name, value, attrs):
    #     datetimepicker_id = 'datetimepicker_{name}'.format(name=name)
    #     if attrs is None:
    #         attrs = {}
    #     attrs['data-target'] = '#{id}'.format(id=datetimepicker_id)
    #     attrs['class'] = 'form-control datetimepicker-input'
    #     context = super().get_context(name, value, attrs)
    #     context['widget']['datetimepicker_id'] = datetimepicker_id
    #     # context['widget']["value"] = "10.04.2022 15:30"
    #     return context

    # def __init__(self, attrs=None):
    #     if attrs is not None:
    #         self.attrs = attrs.copy()
    #     else:
    #         self.attrs = {}

    #     if not 'format' in self.attrs:
    #         # self.attrs['format'] = '%Y-%m-%d %H:%M'
    #         self.attrs['format'] = '%d.%m.%Y %H:%M'

    # def render(self, name, value, attrs=None, renderer=None):
    #     if isinstance(value, datetime.datetime):
    #         value = value.strftime(self.attrs['format'])
    #     return super(forms.TextInput, self).render(name, value, attrs, renderer)
