import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import Client
from channels.layers import get_channel_layer
from django.utils.html import strip_tags
import redis

client = Client.objects.all()
class ChatConsumer(AsyncWebsocketConsumer):
    async def trough_channel(self, channel_name, text_data):
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, { 
                "type": "send.message",
                "text": text_data["message"],
                "user": text_data["sender"],
            })
        
    @database_sync_to_async
    def Backup_message_or_send(self, text_data, my_client : Client): # backup message if ther user offline and send message if the user online 
        redis_client = (redis.Redis)(host='localhost', port=6379, db=2)
        text_data["sender"] = self.scope["user"].username
        if my_client != None:
            if my_client.status == "offline":
                resiver = text_data["user"]
                index = (redis_client.incr)('index') # generate index on redis
                (redis_client.hset)(f'{resiver}:{index}' , mapping=text_data)
            else:
                return "send"
            

    @database_sync_to_async
    def Creat_client(self):
        self.redis_client = (redis.Redis)(host='localhost', port=6379, db=2)
        data = (self.redis_client.keys)("*")
        user = []
        for i in range(len(data)):
            user.append(data[i].decode('utf-8'))
        if (client.filter(username=self.scope["user"].username).exists)(): # if user is alredy have a client model will delete it and creat new channel with online status 
            (client.filter(username=self.scope["user"].username).delete)()
            (client.create)(username=self.scope["user"].username,\
                channel_name=self.channel_name, status="online")
        else:
            (client.create)(username=self.scope["user"].username,\
                        channel_name=self.channel_name, status="online")
        return user
    
    @database_sync_to_async
    def message_send(self, key):
        message = key[0: key.find(":")] # see if the use have a backup message in redis server
        if self.scope["user"].username == message:
            data = (self.redis_client.hgetall)(key)
            data = (list)(data.items())
            data = [[item.decode('utf-8') for item in sublist] for sublist in data]
            data = {key: value for key, value in data}
            json_string = (json.dumps)(data)
            json_string = (json.loads)(json_string)
            (self.redis_client.delete)(key)
            return json_string
            
    async def connect(self):
        user = await self.Creat_client()
        for key in user:
            json_string = await self.message_send(key)
            if (json_string != None):
                await self.trough_channel(self.channel_name, json_string)
        await self.accept()

    async def receive(self, text_data):
        text_data = await sync_to_async (json.loads)(text_data)
        my_client = await sync_to_async(client.get)(username=text_data["user"])
        status = await self.Backup_message_or_send(text_data, my_client)
        if status == "send":
            await self.trough_channel(my_client.channel_name, text_data)

    @database_sync_to_async
    def disconnect(self, event):

        my_client = client.get(username=self.scope["user"].username)
        my_client.update_status("offline")
        my_client.save()

    async def send_message(self, event):
        await self.send(json.dumps({
            'message': (event["text"]),
            'user': (event["user"]),
        }))
