from django.db import models

from user.models import User
from ad.models import Ad


class Bid(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name="Название объявления")
    number_of_person = models.IntegerField(verbose_name="Количество человек")
    number_of_girls = models.IntegerField(verbose_name="Количество девушек")
    number_of_boys = models.IntegerField(verbose_name="Количество парней")
    photos = models.ForeignKey("BidImages", on_delete=models.CASCADE, verbose_name="Фотографии")
    create_ad = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f'{self.pk}'

    def to_json(self):
        return {
            "ad": {
                "id": self.pk,
                "photo_participants": self.photos.photo_participants,
                "photo_alcohol": self.photos.photo_alcohol,
            },
            "user": {
                "id": self.author.pk,
                "username": self.author.username,
                "photo": '/images/' + str(self.author.photo),
            }
        }

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class BidImages(models.Model):
    photo_participants = models.ImageField(upload_to='bids/photo_participants/%Y/%m/%d', verbose_name="Фото участников")
    photo_alcohol = models.ImageField(upload_to='bids/photo_alcohol/%Y/%m/%d', verbose_name="Фото алкоголя")

    def __str__(self):
        return 'Фотографии'

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
