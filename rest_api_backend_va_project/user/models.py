from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

from utils.choices.choices import CITIES, SEX


class Subscription(models.Model):
    author = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name="author_subscriber"
    )
    date_start = models.DateTimeField(auto_now_add=True, verbose_name="Дата начало подписки")
    date_end = models.DateTimeField(verbose_name="Дата конца подписки")

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class User(AbstractUser):
    city = models.CharField(choices=CITIES, max_length=1)
    birth_day = models.DateField(null='2021-03-03')
    sex = models.CharField(choices=SEX, max_length=100)
    photo = models.ImageField(upload_to='avatar/%Y/%m/%d')
    confirm_email = models.BooleanField(default=False)
    confirm_account = models.BooleanField(default=False)
    code_confirm = models.IntegerField(null=True, blank=True, unique=True)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        verbose_name='Подписка',
        null=True,
        blank=True
    )
    last_activity = models.DateTimeField(default=now(), verbose_name="Последний раз в сети")

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.first_name
