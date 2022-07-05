import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AdConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print('Connect (consumer - Ad)')
        self.id_ad = self.scope['url_route']['kwargs']['city']
        self.ad_group_name = 'city_%s' % self.id_ad
        await self.accept()
        await self.channel_layer.group_add(
            self.ad_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        print('Disconnect (consumer - Ad)')
        await self.channel_layer.group_discard(
            self.ad_group_name,
            self.channel_name
        )

    async def ad(self, event):
        print('ad (consumer - Ad)')
        await self.send(text_data=json.dumps({
            'message_to_room': event
        }))
