from django.db import models

from user.models import User
from ad.models import Ad


class Room(models.Model):
    """Model room chat"""
    ad = models.ForeignKey(Ad, verbose_name="Объявление", on_delete=models.CASCADE)
    invited = models.ManyToManyField(User, verbose_name="Участники", related_name="invited_user")
    blocked_user = models.ManyToManyField(
        User,
        blank=True, 
        related_name="blocked_user",
        verbose_name="Заблокированные пользователи"
    )
    voting = models.ManyToManyField(
        "Vote",
        related_name="voting_user",
        default=None,
        blank=True
    )

    class Meta:
        verbose_name = "Комната чата"
        verbose_name_plural = "Комнаты чатов"


class Vote(models.Model):
    """Модель голосования"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор предложения о голосовании")
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_candidate",
        verbose_name="Кандидат"
    )
    votes = models.IntegerField(default=1)
    voted = models.ManyToManyField(
        User, 
        verbose_name="Проголосовавшие пользователи", 
        related_name="voted_users", 
        blank=True
    )

    def to_vote(self, user, action):
        if action == 'up':
            self.votes += 1
            self.voted.add(user)
            self.save() 
        else:
            self.votes -= 1
            self.voted.add(user)
            self.save()
    
    def voting_count(self):
        return self.votes

    def __str__(self):
        return 'Голосование'

    class Meta:
        verbose_name = "Голосования"
        verbose_name_plural = "Голосовании"


class Chat(models.Model):
    """Model chat"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Комната чата")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    text = models.TextField(max_length=500, blank=True, verbose_name="Сообщение")
    images = models.ForeignKey(
        "ImageMessage",
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        null=True,
        verbose_name="Фотографии"
    )
    date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата отправки")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чатов"
        ordering = ['date']


class ImageMessage(models.Model):
    first_image = models.ImageField(upload_to="chat/first_image/%Y/%m/%d", blank=True, verbose_name="Первое фотография")
    second_image = models.ImageField(
        upload_to="chat/second_image/%Y/%m/%d",
        blank=True,
        verbose_name="Вторая фотография"
    )
    date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата отправки")

    def __str__(self):
        return "Фотография"

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ['date']
