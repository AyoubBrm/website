import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Client
from channels.layers import get_channel_layer
from django.utils.html import strip_tags
import redis

class ChatConsumer(AsyncWebsocketConsumer):

    async def trough_channel(self, channel_name, text_data):
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, { 
                "type": "send.message",
                "text": text_data["message"],
                "user": text_data["sender"],
            })

    async def connect(self):

        redis_client = await sync_to_async (redis.Redis)(host='localhost', port=6379, db=0)
        data = await sync_to_async (redis_client.keys)("*")
        user = []
        for i in range(len(data)):
            await sync_to_async(user.append)(data[i].decode('utf-8'))
        
        if await sync_to_async (Client.objects.filter(username=self.scope["user"].username).exists)():
            await sync_to_async (Client.objects.filter(username=self.scope["user"].username).delete)()
            await sync_to_async (Client.objects.create)(username=self.scope["user"].username,\
                channel_name=self.channel_name, status="online")
            for key in user:
                message = key[0: key.find(":")]
                if self.scope["user"].username == message:
                    data = await sync_to_async (redis_client.hgetall)(key)
                    data = await sync_to_async (list)(data.items())
                    data = [[item.decode('utf-8') for item in sublist] for sublist in data]
                    data = {key: value for key, value in data}
                    json_string = await sync_to_async (json.dumps)(data)
                    json_string = await sync_to_async (json.loads)(json_string)
                    await sync_to_async (redis_client.delete)(key)
                    await self.trough_channel(self.channel_name, json_string)
        else:
            await sync_to_async (Client.objects.create)(username=self.scope["user"].username,\
                        channel_name=self.channel_name, status="online")
        await self.accept()

    async def disconnect(self, text_data):

        client = await sync_to_async (Client.objects.get)(username=self.scope["user"].username)
        await sync_to_async (client.update_status)("offline")
        await sync_to_async (client.save)()

    async def receive(self, text_data):
        redis_client = await sync_to_async (redis.Redis)(host='localhost', port=6379, db=0)
        text_data = json.loads(text_data)
        client = await sync_to_async (Client.objects.get)(username=text_data["user"])
        text_data["sender"] = self.scope["user"].username
        if client != None:
            if client.status == "offline":
                resiver = text_data["user"]
                index = await sync_to_async (redis_client.incr)('index')
                await sync_to_async (redis_client.hset)(f'{resiver}:{index}' , mapping=text_data)
            else:
                await self.trough_channel(client.channel_name, text_data)
        
    async def send_message(self, event):
        await self.send(json.dumps({
            'message': (event["text"]),
            'user': (event["user"]),
        }))
