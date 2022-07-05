from django.db.models.signals import pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Chat


@receiver(pre_delete, sender=Chat)
def on_change(sender, instance, using, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{instance.room.pk}", {
            "type": "chat_message",
            "message": [{
                "event": "Delete message",
                "message": f"Сообщение успешно удаленно",
                "id_message": instance.pk
            }]
        }
    )
