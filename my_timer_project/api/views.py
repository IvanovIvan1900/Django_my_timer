import logging
from collections import defaultdict
from datetime import datetime
from functools import partial
from typing import Dict, List, Optional, Tuple, Union

import pytz
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from main.models import Clients, TimeTrack
from main.utility import log_exception
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from api.serializers import TimeTrackerSerializer
# Create your views here.
from api.utily import  html_to_pdf, build_url

# from tomlkit import array


logger = logging.getLogger(f'django.{__name__}')

@log_exception(None)
@api_view(['GET', 'PUT'])
@permission_classes((IsAuthenticated,))
def TimeTreckerDetalView(request, pk):
    if request.method == 'PUT':
        instance = get_object_or_404(TimeTrack, pk=pk)
        if instance is None:
            return Response(f"Error. Time track wich id {pk} is not find",
                status=HTTP_400_BAD_REQUEST)
        serializer = TimeTrackerSerializer(instance=instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors,
                status=HTTP_400_BAD_REQUEST)
        serializer.update(instance=instance, validated_data=serializer.validated_data)
        return Response(serializer.data, status=HTTP_201_CREATED)
    else:
        tt = TimeTrack.objects.filter(pk=pk)
        serializer = TimeTrackerSerializer(tt, many=True)
        return Response(serializer.data)

@log_exception(None)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def TimeTreckerList(request):
    tt = TimeTrack.objects.filter()
    serializer = TimeTrackerSerializer(tt, many=True)
    return Response(serializer.data)

@log_exception(None)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def ClientList(request):
    client_list = Clients.objects.filter(user=request.user)
    if "q" in request.query_params.keys():
        client_list = client_list.filter(name__icontains=request.query_params.get("q"))
    client_list = client_list.all()
    array_of_dic = [{"id":elem.id, "text":elem.name} for elem in client_list]
    data = {"results":  array_of_dic,
    "pagination": {
        "more": False
    }
    }
    return Response(data)


def service_parse_date(date_str:str)->Optional[datetime]:
    result = None
    if date_str:
        try:
            result = datetime.strptime(date_str, "%d.%m.%Y")
            result = result.replace(tzinfo=pytz.utc)
        except Exception as e:
            logger.error(f'Error parse date "{date_str}". Error is "{e}"')
            result = None
    return result

@log_exception(None)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def TimeTrackReport(request):
    t_query = TimeTrack.objects.values("task__client", "task__client__name", "task", "task__name")
    # format date dd.MM.YYYY
    if "date_start" in request.query_params and request.query_params.get("date_start", None) is not None:
        date_value = service_parse_date(request.query_params.get("date_start", None))
        if date_value is not None:
            t_query = t_query.filter(date_stop__gte=date_value)
    if "date_stop" in request.query_params and request.query_params.get("date_stop", None) is not None:
        date_value = service_parse_date(request.query_params.get("date_stop", None))
        if date_value is not None:
            date_value = date_value.replace(hour=23, minute=59, second=59)
            t_query = t_query.filter(date_stop__lte=date_value)
    if "client_id" in request.query_params and request.query_params.get("client_id", None) is not None:
        t_query = t_query.filter(task__client__id=request.query_params.get("client_id", None))
    if "task_name" in request.query_params and request.query_params.get("task_name", None) is not None:
        t_query = t_query.filter(task__name__icontains=request.query_params.get("task_name", None))
    if "only_wichout_account" in request.query_params and request.query_params.get("only_wichout_account", None) is not None and request.query_params.get("only_wichout_account", None).upper() in "TRUE, 1":
        t_query = t_query.filter(date_account__isnull=True)
    


    t_query = t_query.annotate(duration= Sum("duration_sec")).order_by("task__client", "task__name").all()
    array_of_client = []
    dic_of_task = defaultdict(list)
    for elem in t_query:
        dic_data = {"client_id":elem.get("task__client"), "client_name":elem.get("task__client__name"), 
                "task_id":elem.get("task"), "task_name":elem.get("task__name"), "duration":elem.get("duration", 0)}
        dic_of_task[elem.get("task__client__name")].append(dic_data)
    array_of_client = sorted(dic_of_task.keys())
    return Response({"array_of_client":  array_of_client,
        "dic_of_task":dic_of_task,
    })

@log_exception(None)
def check_param_is_present_and_is_not_none(request:Request, param:List[str]) -> Tuple[bool, Optional[Response]]:
    array_error = []
    succes = True
    for elem in param:
        if elem not in request.query_params or request.query_params.get(elem, None) is None:
            succes = False
            array_error.append(f'Param "{elem}" is not present or empty')
    resp = None if succes else Response(data=", ".join(array_error), status=status.HTTP_400_BAD_REQUEST)

    return succes, resp

@log_exception(None)
def qeury_filter_add_filter_to_query(query, settings_report):
    query = query.filter(date_stop__gte=settings_report["date_start"],
        date_stop__lte=settings_report["date_stop"],
        task__id__in=settings_report["task_id_array"])
    if settings_report["only_wichout_account"]:
        query = query.filter(date_account__isnull=True)

    return query


@log_exception(None)
def service_rquest_parse_param(request:Request, mandatory_param:List[str], addition_param:Optional[List[str]])->Tuple[bool, Union[Response,Dict]]:
    succes, resp = check_param_is_present_and_is_not_none(request=request, 
            param=mandatory_param)
    if not succes:
        return succes, resp
    param = mandatory_param
    if addition_param is not None:
        param.extend(addition_param)
    settings_report = {"date_start": service_parse_date(request.query_params.get("date_start", None))}
    if "date_stop" in param:
        settings_report["date_stop"] = service_parse_date(request.query_params.get("date_stop", None)).replace(hour=23, minute=59, second=59)
    if "task_id_array_str" in param:
        settings_report["task_id_array"] = [int(elem) for elem in request.query_params.get("task_id_array_str", "").split(",") if elem]
    if "only_wichout_account" in param:
        settings_report["only_wichout_account"] = request.query_params.get("only_wichout_account", "false") in "true,True,1"
    if "set_date_account" in param:
        settings_report["set_date_account"] = request.query_params.get("set_date_account", "") in "true,True, 1"
    if "redirect" in param:
        settings_report["redirect"] = request.query_params.get("redirect", "") in "true,True, 1"
    if "task_name" in param:
        settings_report["task_name"] = request.query_params.get("task_name", "")
    if "client_id" in param:
        settings_report["client_id"] = request.query_params.get("client_id", "")

    return succes, settings_report

@log_exception(None)
def service_get_context_for_report(request:Request, settings_report: dict)->Dict:
    t_query = TimeTrack.objects.values("task__name", "task__client__full_name")
    t_query = qeury_filter_add_filter_to_query(t_query, settings_report=settings_report)
    t_query = t_query.annotate(duration= Sum("duration_sec")).order_by("task__client__full_name", "task__name").all()

    context= {"total_spend":0, "client_full_name":"", "date_start":settings_report["date_start"],
        "date_stop":settings_report["date_stop"]}
    array_of_task = []
    for i, elem in enumerate(t_query, start=1):
        context["client_full_name"] = elem.get("task__client__full_name", "")
        context["total_spend"] +=elem.get("duration", 0)
        array_of_task.append({"task_name":elem.get("task__name", ""), "spend_time":elem.get("duration", 0), "index":i})
    context["array_time_spend"] = array_of_task

    if settings_report["set_date_account"]:
        date_now = datetime.now(pytz.utc).date()
        r_query = TimeTrack.objects
        # settings_report["only_wichout_account"] = True
        r_query = qeury_filter_add_filter_to_query(r_query, settings_report=settings_report)
        r_query.update(date_account=date_now)


    return context

@log_exception(None)
def get_report(request:Request, type_of_result:str) -> Response:
    succes, settings_report_or_response = service_rquest_parse_param(request=request,
            mandatory_param=["date_start", "date_stop", "task_id_array_str"], addition_param=["only_wichout_account", "set_date_account"])
    if not succes:
        return settings_report_or_response
    context = service_get_context_for_report(request=request, settings_report=settings_report_or_response)
    if type_of_result == "pdf":
        return html_to_pdf("my_timer_main/main/report.html", context)
    else:
        return render(request, 'my_timer_main/main/report.html', context)

@log_exception(None)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def set_account_date(request:Request) -> Response:
    succes, settings_report_or_response = service_rquest_parse_param(request=request,
            mandatory_param=["date_start", "date_stop", "task_id_array_str"], addition_param=["only_wichout_account", "set_date_account",
                    "client_id", "task_name", "redirect"])
    if not succes:
        return settings_report_or_response
    service_get_context_for_report(request=request, settings_report=settings_report_or_response)
    if settings_report_or_response["redirect"]:
        url = build_url('my_timer:report_task_list', {
                    "date_start":settings_report_or_response["date_start"],
                    "date_stop":settings_report_or_response["date_stop"],
                    "client_id":settings_report_or_response["client_id"],
                    "task_name":settings_report_or_response["task_name"],
                    "only_wichout_account":settings_report_or_response["only_wichout_account"],
                 })
        return HttpResponse(url)
    else:
        return HttpResponse('')

@log_exception(None)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_report_pdf(request):
    return get_report(request=request, type_of_result="pdf")

@log_exception(None)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_report_html(request):
    return get_report(request=request, type_of_result="html")

