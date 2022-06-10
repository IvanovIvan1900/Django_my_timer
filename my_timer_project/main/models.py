import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from datetime import datetime as dt
from django.utils import timezone as tz
from .utility import clear_cache_client, active_task_cache_client
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import transaction
# Create your models here.

class MyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    # def delete(self, *args, **kwargs):
    #     a = 4
    #     pass

class Clients(models.Model):
    name = models.CharField(max_length=100, db_index=True,  unique=True, verbose_name='Название')
    full_name = models.CharField(max_length=200, db_index=True,
                verbose_name='Официальное название')
    is_active = models.BooleanField(verbose_name= 'Активный', db_index= True)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT)
    is_delete = models.BooleanField(default=False)

    objects = MyManager()

    class Meta:
        verbose_name_plural = 'Клиенты'
        verbose_name = 'Клиент'
        ordering = ['-name']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_cache_client()

    def __str__(self):
        return self.name

    # @transaction.atomic
    def delete(self, *args, **kwargs):
        autocommit_before = transaction.get_autocommit()
        transaction.set_autocommit(False)
        try:
            self.is_delete = True
            self.save()
            Tasks.objects.filter(client = self).update(is_delete=True)
            query_task = Tasks.objects.filter(client = self).all()
            Comments.objects.filter(task__id__in=query_task).update(is_delete=True)
            TimeTrack.objects.filter(task__id__in=query_task).update(is_delete=True)
            transaction.commit()
        except Exception as e:
            logger = logging.getLogger(f'django.{__name__}.Clients.Delete')
            logger.exception(e)
            transaction.rollback()
        finally:
            transaction.set_autocommit(autocommit_before)


class Tasks(models.Model):
    name = models.CharField(max_length=100, db_index=True,  verbose_name='Название')
    is_active = models.BooleanField(verbose_name= 'Активная', db_index= True)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, db_index= True,
                verbose_name='Клиент')
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                verbose_name='Создана')
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT)
    date_start_plan = models.DateField(verbose_name="Дата старта (план)", null=True)
    is_delete = models.BooleanField(default=False)

    objects = MyManager()

    class Meta:
        verbose_name_plural = 'Задачи'
        verbose_name = 'Задача'
        ordering = ['-created_at']
        unique_together = ('name', 'client')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        active_task_cache_client()

    def __str__(self):
        return f'{self.name} ({self.client.name})'
    
    
    def delete(self, *args, **kwargs):
        autocommit_before = transaction.get_autocommit()
        transaction.set_autocommit(False)
        try:
            self.is_delete = True
            self.save()
            Comments.objects.filter(task__id=self.id).update(is_delete=True)
            TimeTrack.objects.filter(task__id=self.id).update(is_delete=True)
            transaction.commit()
        except Exception as e:
            logger = logging.getLogger(f'django.{__name__}.Tasks.Delete')
            logger.exception(e)
            transaction.rollback()
        finally:
            transaction.set_autocommit(autocommit_before)

# def TimeTracker_post_init(self, *args, **kwargs):
#     instance = kwargs.get('instance', None)

#     kwargs.update(initial={
#         # 'field': 'value'
#         'date_start': dt.now()
#     })

#     super(TimeTrack, self).__init__(*args, **kwargs)

class TimeTrack(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
                        db_index=True)
    date_start = models.DateTimeField(verbose_name='Начало')
    date_stop= models.DateTimeField( verbose_name='Окончание', null=True)
    duration_sec = models.IntegerField(verbose_name="Продолжительность (сек.)")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT, db_index = True)
    is_active = models.BooleanField(verbose_name="Задача в работе", default = False, db_index= True)
    date_account = models.DateField(verbose_name="Дата счета", null=True)
    is_delete = models.BooleanField(default=False)

    objects = MyManager()

    class Meta:
        verbose_name_plural = 'Трек по задачам'
        verbose_name = 'Трек по задаче'
        ordering = ['-date_stop']

    def __str__(self):
        return f'{self.task.name} Продолжительность (сек.) {self.duration_sec}'

    def delete(self, *args, **kwargs):
        # autocommit_before = transaction.get_autocommit()
        # transaction.set_autocommit(False)
        try:
            self.is_delete = True
            self.save()
        except Exception as e:
            logger = logging.getLogger(f'django.{__name__}.TimeTrack.Delete')
            logger.exception(e)
            # transaction.savepoint_rollback(save_point)


    def save(self, *args, **kwargs):
            if self.date_stop and self.date_start:
                self.duration_sec = (self.date_stop - self.date_start).total_seconds()
            if self.date_start and not self.date_stop:
                self.is_active = True
            else:
                self.is_active = False
            super().save(*args, **kwargs)  # Call the "real" save() method.

class Comments(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="Задача")
    content = RichTextUploadingField(verbose_name='Содержание')
    update_at = models.DateTimeField(auto_now=True, db_index=True,
            verbose_name='Дата создания')
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT, db_index = True)
    is_delete = models.BooleanField(default=False)

    objects = MyManager()

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['update_at']

    def delete(self, *args, **kwargs):
        # transaction.set_autocommit(False)
        # save_point = transaction.savepoint()
        try:
            self.is_delete = True
            self.save()
        except Exception as e:
            logger = logging.getLogger(f'django.{__name__}.Comment.Delete')
            logger.exception(e)
            # transaction.savepoint_rollback(save_point)

# signals.post_init.connect(receiver=TimeTracker_post_init, sender=TimeTrack)