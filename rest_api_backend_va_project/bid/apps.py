from django.apps import AppConfig


class BidConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bid'
    verbose_name = 'Заявки'

    def ready(self):
        from . import signals
