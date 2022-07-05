import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rest Framework path
    path('api-auth/', include('rest_framework.urls')),

    # User
    path('api/users/', include('user.urls')),

    # Ad
    path('api/ad/', include('ad.urls')),

    # Bid
    path('api/bid/', include('bid.urls')),

    # Participant
    path('api/participant/', include('participant.urls')),

    # Room chat
    path('api/chat/', include('room_chat.urls')),

    # Token
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/token/verify/', TokenVerifyView.as_view()),

    # Debug toolbar
    path('__debug__/', include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
