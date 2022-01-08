from django.core.cache import caches


def get_qery_client_wich_cahce(class_model):
    cache_qery_key = "client_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        return caches['mem_cache'].get(cache_qery_key)
    else:
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
    else:
        qery = class_model.objects.filter(is_active=True).all()
        caches['mem_cache'].set(cache_qery_key, qery)
        return qery

def active_task_cache_client():
    cache_qery_key = "active_task_qery_cache"
    if caches['mem_cache'].has_key(cache_qery_key):
        caches['mem_cache'].delete(cache_qery_key)
