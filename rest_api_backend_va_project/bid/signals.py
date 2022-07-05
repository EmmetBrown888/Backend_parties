import json
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Bid


@receiver(post_save, sender=Bid)
def on_change(sender, instance, created, raw, **kwargs):
    if created:  # Create a new bid
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{str(instance.ad.author.pk)}", {
                "type": "user_gossip",
                "event": "Create bid",
                "message": f"Пользователь {instance.author.username} проявил желание участвовать в вашей вечеринке {instance.ad.title}",
                "bid": {
                    "bid_id": instance.pk,
                    "author_bid": {
                        "id": instance.author.pk,
                        "username": instance.author.username,
                        "photo": '/images/' + str(instance.author.photo)
                    },
                    "data": {
                        "number_of_person": instance.number_of_person,
                        "number_of_girls": instance.number_of_girls,
                        "number_of_boys": instance.number_of_boys,
                        "photos": {
                            "photo_participants": '/images/' + str(instance.photos.photo_participants),
                            "photo_alcohol": '/images/' + str(instance.photos.photo_alcohol),
                        }
                    }
                }
            }
        )
