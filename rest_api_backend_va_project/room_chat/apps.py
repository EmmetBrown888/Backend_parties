from django.apps import AppConfig


class RoomChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'room_chat'
    verbose_name = 'Мессенджер'

    def ready(self):
        from . import signals
