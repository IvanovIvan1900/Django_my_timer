from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Clients(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True,
                verbose_name='Название')
    full_name = models.CharField(max_length=200, db_index=True,
                verbose_name='Официальное название')
    is_active = models.BooleanField(verbose_name= 'Активный', db_index= True)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT)


    class Meta:
        verbose_name_plural = 'Клиенты'
        verbose_name = 'Клиент'
        ordering = ['-name']

    def __str__(self):
        return self.name

class Tasks(models.Model):
    name = models.CharField(max_length=50, db_index=True, unique=True,
                verbose_name='Название')
    is_active = models.BooleanField(verbose_name= 'Активная', db_index= True)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE,
                verbose_name='Клиент')
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                verbose_name='Создана')
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT)
    class Meta:
        verbose_name_plural = 'Задачи'
        verbose_name = 'Задача'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.client.name})'

class TimeTrack(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
                        db_index=True)
    date_start = models.DateTimeField(auto_now_add=True, verbose_name='Начало')
    date_stop= models.DateTimeField(auto_now_add=True, verbose_name='Окончание')
    duration_sec = models.IntegerField(verbose_name="Продолжительность (сек.)")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = 'Трек по задачам'
        verbose_name = 'Трек по задаче'
        ordering = ['-date_stop']