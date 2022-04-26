from collections import defaultdict
from datetime import datetime
from functools import partial
import logging
from typing import List, Optional, Tuple
from rest_framework.request import Request

import pytz
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from main.models import Clients, TimeTrack
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from tomlkit import array

from api.serializers import TimeTrackerSerializer
# Create your views here.
from api.utily import html_to_pdf

logger = logging.getLogger(f'django.{__name__}')
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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def TimeTreckerList(request):
    tt = TimeTrack.objects.filter()
    serializer = TimeTrackerSerializer(tt, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def ClientList(request):
    client_list = Clients.objects.filter(user=request.user)
    if "q" in request.query_params.keys():
        client_list = client_list.filter(name__icontains=request.query_params.get("q"))
    client_list = client_list.all()
    array_of_dic = []
    for elem in client_list:
        array_of_dic.append({"id":elem.id, "text":elem.name})
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
    array_of_client = [elem for elem in dic_of_task.keys()]
    array_of_client.sort()
    return Response({"array_of_client":  array_of_client,
        "dic_of_task":dic_of_task,
    })

def check_param_is_present_and_is_not_none(request:Request, param:List[str]) -> Tuple[bool, Optional[Response]]:
    array_error = []
    succes = True
    for elem in param:
        if elem not in request.query_params or request.query_params.get(elem, None) is None:
            succes = False
            array_error.append(f'Param "{elem}" is not present or empty')
    resp = None if succes else Response(", ".join(array_error), status=status.HTTP_400_BAD_REQUEST)

    return succes, resp

def qeury_filter_add_filter_to_query(query, settings_report):
    query = query.filter(date_stop__gte=settings_report["date_start"],
        date_stop__lte=settings_report["date_stop"],
        task__id__in=settings_report["task_id_array"])
    if settings_report["only_wichout_account"]:
        query = query.filter(date_account__isnull=True)

    return query

def get_report(request:Request, type_of_result:str) -> Response:
    succes, resp = check_param_is_present_and_is_not_none(request=request, param=["date_start", "date_stop", "task_id_array_str", "set_date_account"])
    if not succes:
        return resp
    settings_report = {"date_start": service_parse_date(request.query_params.get("date_start", None))}
    settings_report["date_stop"] = service_parse_date(request.query_params.get("date_stop", None)).replace(hour=23, minute=59, second=59)
    settings_report["task_id_array"] = [int(elem) for elem in request.query_params.get("task_id_array_str", "").split(",") if elem]
    settings_report["only_wichout_account"] = request.query_params.get("only_wichout_account", "") in "true,True, 1"
    settings_report["set_date_account"] = request.query_params.get("set_date_account", "") in "true,True, 1"

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
        settings_report["only_wichout_account"] = True
        r_query = qeury_filter_add_filter_to_query(r_query, settings_report=settings_report)
        r_query.update(date_account=date_now)

    if type_of_result == "pdf":
        return html_to_pdf("my_timer_main/main/report.html", context)
    else:
        return render(request, 'my_timer_main/main/report.html', context)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_report_pdf(request):
    return get_report(request=request, type_of_result="pdf")

@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
def get_report_html(request):
    return get_report(request=request, type_of_result="html")

