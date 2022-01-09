import logging
from django.core.cache import caches
from datetime import datetime as dt
from django.utils import timezone as tz
from django.utils.timezone import get_current_timezone, make_aware
import logging

logger = logging.getLogger(__name__)

def get_qery_client_wich_cahce(class_model):
    cache_qery_key = "client_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        return caches['mem_cache'].get(cache_qery_key)
    qery = class_model.objects.all()
    caches['mem_cache'].set(cache_qery_key, qery)
    return qery

def clear_cache_client():
    cache_qery_key = "client_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        caches['mem_cache'].delete(cache_qery_key)

def get_qery_active_task_wich_cahce(class_model):
    cache_qery_key = "active_task_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        return caches['mem_cache'].get(cache_qery_key)
    qery = class_model.objects.select_related().filter(is_active=True).all()
    caches['mem_cache'].set(cache_qery_key, qery)
    return qery

def active_task_cache_client():
    cache_qery_key = "active_task_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        caches['mem_cache'].delete(cache_qery_key)

def date_convert_from_string(str_value, date_format = None):
    # logger = logging.getLogger("utils")
    dt_result = None
    if date_format is None:
        date_format = "%d.%m.%Y"
    try:
        dt_result = dt.strptime(str_value, date_format)
        dt_result = make_aware(dt_result)
        # dt_result = dt_result.replace(tzinfo=get_current_timezone())
    except Exception as e:
        logger.error(f'Error convert string {str_value}, to date. Error is "{e}"')
    
    return dt_result

def date_end_of_day(dt_in):
    dt_result = None
    if isinstance(dt_in, dt):
        dt_result = dt_in.replace(hour=23, minute=59, second=59, microsecond=999)
    return dt_result