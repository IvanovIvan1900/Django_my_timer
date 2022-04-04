import datetime
import uuid
from datetime import timedelta
import pytest
from django.contrib.auth.models import User
import pytz
# import django
# from django.conf import settings
# SETTINGS = dict((key,val) for key, val in locals().items() if key.isupper())
# if not settings.configured:
#     settings.configure(**SETTINGS)
# django.setup()

from main.models import Clients, Tasks, TimeTrack


@pytest.fixture
def test_password():
   return '!!Strong-test-pass!!'

@pytest.fixture
def create_user(db, django_user_model, test_password):
   def make_user(**kwargs):
       kwargs['password'] = test_password
       if 'username' not in kwargs:
           kwargs['username'] = str(uuid.uuid4())
       return django_user_model.objects.create_user(**kwargs)
   return make_user

@pytest.fixture
def user_1(create_user):
    return create_user(username='user_1')

@pytest.fixture
def user_2(create_user):
    return create_user(username='user_2')

@pytest.fixture
def auto_login_user(db, client, create_user, test_password, user_1):
   def make_auto_login(user=None):
       if user is None:
           user = create_user()
       client.login(username=user.username, password=test_password)
       return client, user
   return make_auto_login

@pytest.fixture
def client_1(db, user_1:User)->Clients:
    dic_of_data = {
        "name":"client 1",
        "full_name":"Full name client 1",
        "is_active":True,
        "user":user_1,
    }
    return Clients.objects.create(**dic_of_data)

@pytest.fixture
def client_2_inactive(db, user_1:User)->Clients:
    dic_of_data = {
        "name":"client 2 inactive",
        "full_name":"Full name client 2 inactive",
        "is_active":False,
        "user":user_1,
    }
    return Clients.objects.create(**dic_of_data)

@pytest.fixture
def date_today():
    return datetime.datetime.now(pytz.utc)

@pytest.fixture
def date_yesterday():
    return (datetime.datetime.now(pytz.utc)-timedelta(days=1))

@pytest.fixture
def date_tomorrow():
    return (datetime.datetime.now(pytz.utc)+timedelta(days=1))

@pytest.fixture
def task_1_user_1(db, user_1:User, client_1:Clients, date_today:datetime.datetime)->Tasks:
    dic_of_data = {
        "name":"Test task. Active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_today,
        "user":user_1,
        "date_start_plan":date_today,
    }
    return Tasks.objects.create(**dic_of_data)

@pytest.fixture
def task_2_user_2(db, user_2:User, client_1:Clients, date_today:datetime.datetime)->Tasks:
    dic_of_data = {
        "name":"Test task 2. Active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_today,
        "user":user_2,
        "date_start_plan":date_today,
    }
    return Tasks.objects.create(**dic_of_data)

@pytest.fixture
def task_list_of_task(db, user_1:User, user_2:User, client_1:Clients, client_2_inactive:Clients, date_today:datetime.datetime, date_yesterday:datetime.datetime,
    date_tomorrow:datetime.datetime)->dict:
    """return dic of task:
        "task_plan_today":
        "task_plan_tomorrow":
        "task_plan_yesterday":
        "task_wichout_plan"
        "task_all":
    """    
    dic_of_result = {"task_plan_today":[], "task_plan_tomorrow":[], "task_plan_yesterday":[],
        "task_wichout_plan":[], "task_all":[]}
    
    dic_of_data = {
        "name":"",
        "is_active":False,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_today,
        "user":user_1,
        "date_start_plan":date_today,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_plan_today"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 1/1. Yesterday is active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_today,
        "user":user_1,
        "date_start_plan":date_today,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    dic_of_data["name"] = dic_of_data["name"]+"1"
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_plan_today"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 1/1. Yesterday is active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_today,
        "user":user_1,
        "date_start_plan":date_today,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    dic_of_data["name"] = dic_of_data["name"]+"2"
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_plan_today"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 2. Active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_yesterday,
        "user":user_1,
        "date_start_plan":date_yesterday,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_plan_yesterday"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 3. Active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_tomorrow,
        "user":user_1,
        "date_start_plan":date_tomorrow,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_plan_tomorrow"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 4. Active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_tomorrow,
        "user":user_1,
        "date_start_plan":None,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_wichout_plan"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 5. Active",
        "is_active":True,
        "client":client_1,
        "description":"Desctiption test task. Task is active",
        "created_at":date_tomorrow,
        "user":user_2,
        "date_start_plan":None,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_wichout_plan"].append(task)
    dic_of_result["task_all"].append(task)

    dic_of_data = {
        "name":"Test task list 5. Active",
        "is_active":True,
        "client":client_2_inactive,
        "description":"Desctiption test task. Task is active",
        "created_at":date_tomorrow,
        "user":user_2,
        "date_start_plan":None,
    }
    dic_of_data["name"] = f'Is active {dic_of_data["is_active"]}, client {dic_of_data["client"]}, user {dic_of_data["user"]}, date plan {dic_of_data["date_start_plan"]}'
    task = Tasks.objects.create(**dic_of_data)
    dic_of_result["task_wichout_plan"].append(task)
    dic_of_result["task_all"].append(task)

    return dic_of_result


@pytest.fixture
def get_list_of_time_tracker(db, task_list_of_task:dict, date_today: datetime.datetime, user_2:User)->list[TimeTrack]:
    list_out:list[TimeTrack] = []
    date_start = date_today-timedelta(hours=1, minutes=20)
    date_stop = date_today
    dic_of_data = {
        "task": task_list_of_task["task_plan_today"][0],
        "date_start": date_start,
        "date_stop": date_stop,
        "user": task_list_of_task["task_plan_today"][0].user,
        "is_active": False,
    }
    list_out.append(TimeTrack.objects.create(**dic_of_data))

    dic_of_data["task"] = task_list_of_task["task_plan_today"][1]
    dic_of_data["user"] = dic_of_data["task"].user
    dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(minutes=10)
    dic_of_data["is_active"] = True
    list_out.append(TimeTrack.objects.create(**dic_of_data))

    dic_of_data["task"] = task_list_of_task["task_plan_today"][2]
    dic_of_data["user"] = dic_of_data["task"].user
    dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(days=10)
    dic_of_data["date_stop"] = dic_of_data["date_stop"]-timedelta(days=10)
    dic_of_data["is_active"] = True
    list_out.append(TimeTrack.objects.create(**dic_of_data))

    dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(minutes=10)
    dic_of_data["date_stop"] = dic_of_data["date_stop"]-timedelta(minutes=10)
    list_out.append(TimeTrack.objects.create(**dic_of_data))

    dic_of_data["task"] = task_list_of_task["task_wichout_plan"][1]
    dic_of_data["user"] = dic_of_data["task"].user
    list_out.append(TimeTrack.objects.create(**dic_of_data))

    dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(minutes=10)
    dic_of_data["date_stop"] = dic_of_data["date_stop"]-timedelta(minutes=10)
    list_out.append(TimeTrack.objects.create(**dic_of_data))

    list_inactive_task = [task for task in task_list_of_task["task_all"] if not task.is_active]
    if len(list_inactive_task) > 0:
        dic_of_data["task"] =list_inactive_task[0]
        dic_of_data["user"] = dic_of_data["task"].user
        list_out.append(TimeTrack.objects.create(**dic_of_data))

        dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(minutes=10)
        dic_of_data["date_stop"] = dic_of_data["date_stop"]-timedelta(minutes=10)
        dic_of_data["task"] =list_inactive_task[len(list_inactive_task)-1]
        dic_of_data["user"] = dic_of_data["task"].user
        list_out.append(TimeTrack.objects.create(**dic_of_data))

    list_user_2_task = [task for task in task_list_of_task["task_all"] if task.user == user_2]
    if len(list_user_2_task) > 0:
        dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(minutes=10)
        dic_of_data["date_stop"] = dic_of_data["date_stop"]-timedelta(minutes=10)
        dic_of_data["task"] =list_user_2_task[len(list_user_2_task)-1]
        dic_of_data["user"] = dic_of_data["task"].user
        list_out.append(TimeTrack.objects.create(**dic_of_data))

        dic_of_data["date_start"] = dic_of_data["date_start"]-timedelta(hours=1, minutes=10)
        dic_of_data["date_stop"] = dic_of_data["date_stop"]-timedelta(minutes=10)
        # dic_of_data["task"] =list_user_2_task[0]
        dic_of_data["user"] = dic_of_data["task"].user
        list_out.append(TimeTrack.objects.create(**dic_of_data))

    return list_out
