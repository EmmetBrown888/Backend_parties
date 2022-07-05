from django.db.models.signals import pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import User


#  Уведомление о создание и изменения пользователя
@receiver(pre_save, sender=User)
def on_change(sender, instance: User, **kwargs):
    print('sender (on_change() User - signals.py) -> ', sender)
    print('instance (on_change() User - signals.py) -> ', instance)

    if instance.id is None:  # Create a new user
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{str(instance.pk)}", {
                "type": "user.gossip",
                "event": "New User",
                "username": instance.username
            }
        )
    else:
        previous = User.objects.get(id=instance.id)
        print('previous (on_change() User - signals.py) -> ', previous)
        if previous.confirm_account != instance.confirm_account:  # check on change field
            if instance.confirm_account:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{str(instance.pk)}", {
                        "type": "user.gossip",
                        "event": "Success confirm account",
                        "message": "Ваш аккаунт успешно подтвержден"
                    }
                )
            else:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{str(instance.pk)}", {
                        "type": "user.gossip",
                        "event": "Error confirm account",
                        "message": "Ваш аккаунт не подтвержден"
                    }
                )
