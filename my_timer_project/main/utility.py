from functools import wraps
import logging
from datetime import datetime as dt

from django.core.cache import caches
from django.utils import timezone as tz
from django.utils.timezone import get_current_timezone, make_aware

import sys


logger = logging.getLogger(f'django.{__name__}')
# logger.error('test logger')

def log_exception(name_log:str = None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                return view_func(*args, **kwargs)
            except Exception as e:
                nonlocal name_log
                if name_log is None:
                    name_log = f'{__name__}.{view_func.__name__}'
                logger = logging.getLogger(f'django.{name_log}')
                logger.exception(e)
        return wrapper
    return decorator
    
@log_exception(None)
def get_qery_client_wich_cahce(class_model):
    # иначе при миграции он пытается выполнить запрос
    if ('makemigrations' in sys.argv or 'migrate' in sys.argv):
        return None
    cache_qery_key = "client_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        return caches['mem_cache'].get(cache_qery_key)
    qery = class_model.objects.all()
    caches['mem_cache'].set(cache_qery_key, qery)
    return qery

@log_exception(None)
def clear_cache_client():
    cache_qery_key = "client_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        caches['mem_cache'].delete(cache_qery_key)

@log_exception(None)
def get_qery_active_task_wich_cahce(class_model):
    cache_qery_key = "active_task_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        return caches['mem_cache'].get(cache_qery_key)
    qery = class_model.objects.select_related().filter(is_active=True).all()
    caches['mem_cache'].set(cache_qery_key, qery)
    return qery

@log_exception(None)
def active_task_cache_client():
    cache_qery_key = "active_task_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        caches['mem_cache'].delete(cache_qery_key)

@log_exception(None)
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

@log_exception(None)
def date_end_of_day(dt_in):
    return dt_in.replace(hour=23, minute=59, second=59, microsecond=999) if isinstance(dt_in, dt) else None

@log_exception(None)
def count_active_task_add():
    name_cache = "cunt_active_task"
    active_task_init()
    caches['mem_cache'].set(name_cache, caches['mem_cache'].get(name_cache)+1)

@log_exception(None)
def count_active_task_minus():
    name_cache = "cunt_active_task"
    active_task_init()
    curr_count = caches['mem_cache'].get(name_cache)
    if curr_count == 0:
        logger.error('Function "count_active_task_minus", but in cache is 0')
    caches['mem_cache'].set(name_cache, curr_count-1)

@log_exception(None)
def active_task_init():
    from main.models import TimeTrack
    cache_name = "cunt_active_task"
    cache = caches['mem_cache']

    count_active_task = cache.get(cache_name, None)
    if count_active_task is None:
        count_active_task = TimeTrack.objects.filter(is_active = True).count()
        cache.set(cache_name, count_active_task)
        logger = logging.getLogger(f'django.{__name__}.debug.init_cache')
        logger.warning("init cache active task")



#def log_exception(name_log:str = None):
