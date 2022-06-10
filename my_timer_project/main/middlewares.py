from django.contrib.staticfiles import finders
from django.core.cache import caches
from main.models import TimeTrack
from main.utility import log_exception


# @log_exception(None)
# class FavIconMiddleware:
#     cache_name = "cunt_active_task"
#     # def service_get_local_path(self, path_to_static:str)->str:
#     #     return  finders.find(path_to_static)
#     #     # return finders.searched_locations

#     # def load_favicon_to_cahce(self):
#     #     path_to_ico = self.service_get_local_path('main/favicon.ico')
#     #     if path_to_ico is not None:
#     #         image_data = open(path_to_ico, "rb").read()
#     #         caches['mem_cache'].set("favicon", image_data)
#     #     path_to_ico_run = self.service_get_local_path('main/favicon_run.ico')
#     #     if path_to_ico_run is not None:
#     #         image_data_run = open(path_to_ico_run, "rb").read()
#     #         caches['mem_cache'].set("favicon_run", image_data_run)

#     def __init__(self, next):
#         self.next = next
#         # self.load_favicon_to_cahce()
#         self.cache = caches['mem_cache']
#         self.cache.set(self.cache_name, -1)
#         # Здесь можно выполнить какую-либо инициализацию

#     def __call__(self, request):
#         if self.cache.get(self.cache_name) <0:
#             self.cache.set(self.cache_name, TimeTrack.objects.filter(is_active = True).count())
#         response = self.next(request)
#         return response
#         # response = self.next(request)
#         # return response

#     def process_template_response(self, request, response):
#         response.context_data['title'] = 'We changed the title'
#         return response

@log_exception(None)
def FavIcon(request):
    cache_name = "cunt_active_task"
    cache = caches['mem_cache']
    has_active_task = False
    if not cache.has_key(cache_name):
        cache.set(cache_name, -1)
    
    count_active_task = cache.get(cache_name)
    if count_active_task < 0:
        count_active_task = TimeTrack.objects.filter(is_active = True).count()
        cache.set(cache_name, count_active_task)

    has_active_task = (count_active_task >0)
    
    return {'has_active_task':has_active_task}
    