from django.db.models.signals import pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Ad


#  Уведомление о создание и изменения объявления
@receiver(pre_save, sender=Ad)
def on_change(sender, instance, **kwargs):
    if instance.id is None:  # Create a new ad
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_id_{instance.author.pk}", {
                "type": "ad",
                "event": "Create ad",
                "username": instance.author.username,
                "ad_title": instance.title
            }
        )
    else:
        previous = Ad.objects.get(id=instance.id)

        if previous.is_published != instance.is_published:  # check on change field
            if instance.is_published:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"city_{instance.city}", {
                        "type": "ad",
                        "event": "Ad published",
                        "message": "Объявление было успешно опубликованно",
                        "geolocation": previous.geolocation,
                        "ad": {
                            "author": {
                                "id": previous.author.pk,
                            },
                            "id_ad": previous.pk
                        }
                    }
                )
