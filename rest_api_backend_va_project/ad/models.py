import json
from django.db import models

from user.models import User
from utils.choices.choices import CITIES


class MyManager(models.Manager):
    def custom_filter(self, **kwargs):
        kwargs['is_published'] = True
        return super().get_queryset().filter(**kwargs)

    def custom_order_by(self, *args):
        args = ('party_date',) + args
        return super().get_queryset().order_by(*args)


class Ad(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название объявления")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    city = models.CharField(choices=CITIES, max_length=1, verbose_name="Город")
    geolocation = models.CharField(blank=True, null=True, max_length=100)
    number_of_person = models.IntegerField(verbose_name="Количество человек")
    number_of_girls = models.IntegerField(verbose_name="Количество девушек")
    number_of_boys = models.IntegerField(verbose_name="Количество парней")
    party_date = models.DateTimeField(verbose_name="Дата вечеринки")
    participants = models.ManyToManyField(User, verbose_name="Участники", related_name="participant_users")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    create_ad = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.title

    def to_json(self):
        def participants_to_json(obj):
            return {
                'id': obj.pk,
                'photo': '/images/' + str(obj.photo)
            }

        participant = []
        for element in self.participants.all():
            result = participants_to_json(element)
            participant.append(result)

        return {
            "id": self.pk,
            "title": self.title,
            "author": {
                "id": self.author.pk,
                "photo": '/images/' + str(self.author.photo)
            },
            "number_of_person": self.number_of_person,
            "number_of_girls": self.number_of_girls,
            "number_of_boys": self.number_of_boys,
            "party_date": json.dumps(self.party_date, indent=4, sort_keys=True, default=str),
            "participants": participant,
        }

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    objects = models.Manager()
    custom_manager = MyManager()
