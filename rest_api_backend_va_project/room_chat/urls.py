from django.urls import path
from .views import *

urlpatterns = [
    path('', MyRooms.as_view(), name='index'),
    path('vote/create/', VoteCreate.as_view(), name='vote_create'),
    path('vote/', Voting.as_view(), name='vote'),
    path('messages/<int:pk>/', Messages.as_view(), name='messages'),
    path('messages/remove/<int:room_id>/<int:id_message>/', MessageRejected.as_view()),
]
