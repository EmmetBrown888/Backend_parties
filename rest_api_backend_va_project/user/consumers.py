from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json


class NoseyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('Connect (consumer) USER')
        self.id_user = self.scope['url_route']['kwargs']['user']
        self.user_group_name = 'user_%s' % self.id_user

        await self.accept()
        await self.channel_layer.group_add(
            self.user_group_name, 
            self.channel_name
        )
        print(f"Added {self.channel_name} channel to gossip")

    async def disconnect(self, close_code):
        print('Disconnect (consumer)')
        await self.channel_layer.group_discard(
            self.user_group_name, 
            self.channel_name
        )

    async def user_gossip(self, event):
        print('user_gossip (consumer)')
        await self.send(text_data=json.dumps({
            'message_to_room': event
        }))
