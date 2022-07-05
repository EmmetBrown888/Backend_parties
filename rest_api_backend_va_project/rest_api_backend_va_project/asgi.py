import os
from django.urls import path
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from room_chat.chatmiddleware import JwtAuthMiddleware
from room_chat.consumers import ChatConsumer
from user.consumers import NoseyConsumer
from ad.consumers import AdConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_backend_va_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter([
            path('ws/chat/<room_name>/', ChatConsumer.as_asgi()),
            path('ws/notification/user/<int:user>/', NoseyConsumer.as_asgi()),
            path('ws/notification/ad/<int:city>/', AdConsumer.as_asgi()),
        ])
    ),
})
