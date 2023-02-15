import json
from channels.generic.websocket import WebsocketConsumer
import base64
from .models import PiDevice
from django.utils import timezone
import os
import io
from django.core.files.images import ImageFile
from channels.layers import get_channel_layer
from django.conf import settings
from asgiref.sync import async_to_sync
# open_socket_connections = {}

def send_reboot_to_channel(channel_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        "type": "do.reboot",
        # "text": "Hello there!",
    })


class ChatConsumer(WebsocketConsumer):
    def do_reboot(self, event):
        print('rebooting')
        self.send(text_data=json.dumps({
            'type': 'command',
            'command': 'reboot'
        }))
    
    
    
    
    def connect(self):
        self.chat_room = self.scope['url_route']['kwargs']['uid']
        self.group_name = 'chat_%s' % self.chat_room
        
        # await self.channel_layer.group_add(
        #     self.group_name,
        #     self.channel_name
        # )
        # await self.accept()
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        device_id = self.chat_room
        tv_device, created = PiDevice.objects.get_or_create(device_id=device_id)
        self.tv_device = tv_device
        self.tv_device.group_channel_name = self.group_name
        self.tv_device.save()
        self.accept()
        
    


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        self.tv_device.socket_status_updated = timezone.now()
        if(message_type == 'status'):
            raw_image = text_data_json['data']['img']
            raw_image = base64.b64decode(raw_image)
            
            self.tv_device.cec_hdmi_status = text_data_json['data']['hdmi_status']
            
            self.tv_device.remote_last_image = ImageFile(io.BytesIO(raw_image), 'image.jpg')
            self.tv_device.remote_last_image_updated = timezone.now()
        self.tv_device.save()
        print(self.tv_device.id, ' saved')
    
    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        self.tv_device.socket_status_updated = timezone.now()
        self.tv_device.is_socket_connected = False
        self.tv_device.group_channel_name = None
        self.tv_device.save()