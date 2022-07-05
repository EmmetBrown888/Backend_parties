from rest_framework import serializers

from .models import Room, Chat, ImageMessage
from ad.serializers import AdRoomChatSerializer
from user.serializers import UserRoomChatSerializer


class RoomSerializers(serializers.ModelSerializer):
    ad = AdRoomChatSerializer()
    invited = UserRoomChatSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ('id', 'ad', 'invited')


class ImagesMessage(serializers.ModelSerializer):
    class Meta:
        model = ImageMessage
        fields = ('first_image', 'second_image')


class ChatSerializer(serializers.ModelSerializer):
    user = UserRoomChatSerializer(read_only=True)
    images = ImagesMessage()

    class Meta:
        model = Chat
        fields = ('id', 'text', 'date', 'room', 'user', 'images')
