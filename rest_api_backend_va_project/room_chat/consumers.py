import json
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import DenyConnection
from channels.db import database_sync_to_async

from .models import Chat, Room, ImageMessage
from user.models import User
from utils.convert_base64.convert_base64_to_django import convert_base64_to_django_model


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('Connect (consumer - Chat)')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope["user"]

        print('self.room_group_name', self.room_group_name)

        await self.check_user()  # Check user authentication

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print('Disconnect (consumer - Chat)')

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print('receive (consumer - Chat)')
        text_data_from_user = json.loads(text_data)
        new_message = await self.create_message(text_data_from_user)

        data = {
            'event': 'Create message',
            'message_id': new_message.pk,
            'user_id': new_message.user.pk,
            'username': new_message.user.username,
            'photo': '/images/' + str(new_message.user.photo),
            'text': new_message.text,
            'first_image': '/images/' + str(new_message.images.first_image) if text_data_from_user['images']['first_image'] else "",
            'second_image': '/images/' + str(new_message.images.second_image) if text_data_from_user['images']['second_image'] else "",
            'created_at': new_message.date.strftime('%Y-%m-%d %H:%m'),
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': [data]
            }
        )

    async def chat_message(self, event):
        print('chat_message (consumer - Chat)')
        event_message = event['message'][0]['event']

        if event_message == 'Create message':
            await self.send(text_data=json.dumps({
                'message_to_room': event['message']
            }))
        elif event_message == 'Delete message':
            await self.send(text_data=json.dumps({
                'message_to_room': event['message']
            }))

    @database_sync_to_async
    def create_message(self, data):
        print('create_message (consumer - Chat)')
        text = data['message']
        first_image = data['images']['first_image']
        second_image = data['images']['second_image']
        room = Room.objects.get(pk=self.room_name)
        user = User.objects.get(pk=self.user.pk)

        if first_image or second_image:
            first_image_decode = convert_base64_to_django_model(first_image) if first_image else ""
            second_image_decode = convert_base64_to_django_model(second_image) if second_image else ""

            images = ImageMessage.objects.create(
                first_image=first_image_decode if first_image else None,
                second_image=second_image_decode if second_image else None
            )

            create_new_message = Chat.objects.create(
                room=room,
                user=user,
                text=text,
                images=images
            )

            return create_new_message

        create_new_message = Chat.objects.create(
            room=room,
            user=user,
            text=text,
            images=None
        )

        return create_new_message

    @database_sync_to_async
    def check_user(self):  # Check user authentication and exists in the room
        if self.scope['user'] == AnonymousUser():
            raise DenyConnection("Такого пользователя не существует")

        user_in_room = Room.objects.filter(Q(pk=self.room_name) & Q(invited__pk=self.user.pk)).exists()

        if not user_in_room:
            raise DenyConnection('Пользователя нет в данной комнате')
