from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login
from account.models import UserProfile, Bote

import json

class UserOnlineStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_email = self.scope['url_route']['kwargs']['user_email']
        self.room_group_name = f"online_status"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        connected_user = await sync_to_async(self.__connect_user, thread_sensitive=True)(self.user_email)
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "updateuserstatus",
            "text": connected_user
        })

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        disconnected_user = await sync_to_async(self.__disconnect_user, thread_sensitive=True)(self.user_email)
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "updateuserstatus",
            "text": disconnected_user
        })
        # await database_sync_to_async(self.scope["session"].pop)("user")

    async def updateuserstatus(self, event):
        new_data = event['text']
        print(new_data)
        await self.send(json.dumps(new_data))

    def __connect_user(self, user):
        profile_user = Bote.objects.get(email=user)
        return UserProfile().connect_user(profile_user)

    def __disconnect_user(self, user):
        profile_user = Bote.objects.get(email=user)
        return UserProfile().discount_user(profile_user)

class ConversationMessageConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"conversation_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def sendmessage(self, event):
        new_data = event['text']
        await self.send(json.dumps(new_data))

class ChatCallRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['call_id']
        self.room_group_name = f"callroom_{self.room_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        receive_data = json.loads(text_data)
        print(receive_data)
        print("\n\n")
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "send_sdp",
            "text": receive_data
        })

    async def send_sdp(self, event):
        send_data = event['text']
        print(send_data)
        await self.send(json.dumps(send_data))