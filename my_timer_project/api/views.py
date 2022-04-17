from collections import defaultdict
from datetime import datetime
from functools import partial
from typing import Optional
from django.shortcuts import get_object_or_404, render
import pytz
from api.serializers import TimeTrackerSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
from main.models import Clients, TimeTrack
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
# Create your views here.

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
            result = None
    return result

@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
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
    if "only_wichout_account" in request.query_params and request.query_params.get("only_wichout_account", None) is not None:
        if request.query_params.get("only_wichout_account", None).upper() in "TRUE, 1":
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
