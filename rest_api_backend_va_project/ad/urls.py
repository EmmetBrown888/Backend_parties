from django.urls import path

from .views import *

urlpatterns = [
    # Get all ads for map
    path('all', AdListView.as_view()),

    # Create ad
    path('create', AdCreateView.as_view()),

    # Change ad
    path('update/<int:pk>/', AdUpdateView.as_view()),

    # Get ad for pk
    path('ad/<int:pk>/', AdRetrieveAPIView.as_view()),

    # Delete ad for pk
    path('remove/<int:pk>', AdDestroyAPIView.as_view()),

    # Get all my ads
    path('my_ads/', MyAdsListAPIView.as_view()),
]
