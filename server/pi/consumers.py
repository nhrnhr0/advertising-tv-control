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
from channels.db import database_sync_to_async

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
    
    
    # @database_sync_to_async
    # def get_tv_device(self, device_id):
        
    #     return tv_device
    
    def update_tv_device(self, device_id,args_dict):
        tv_device, created = PiDevice.objects.get_or_create(device_id=device_id)
        # if cec_hdmi_status:
        #     tv_device.cec_hdmi_status = cec_hdmi_status
        # if remote_last_image:
        #     tv_device.remote_last_image = remote_last_image
        # if socket_status_updated:
        #     tv_device.socket_status_updated = socket_status_updated
        # if is_socket_connected:
        #     tv_device.is_socket_connected = is_socket_connected
        # if group_channel_name:
        #     tv_device.group_channel_name = group_channel_name
        if args_dict:
            for key, value in args_dict.items():
                setattr(tv_device, key, value)
        
            tv_device.save()
        print(tv_device.id, ' saved')
    
    def connect(self):
        self.chat_room = self.scope['url_route']['kwargs']['uid']
        self.group_name = 'chat_%s' % self.chat_room
        self.device_id = self.chat_room
        # await self.channel_layer.group_add(
        #     self.group_name,
        #     self.channel_name
        # )
        # await self.accept()
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        # tv_device, created = PiDevice.objects.get_or_create(device_id=device_id)
        # self.tv_device = tv_device
        # self.tv_device.group_channel_name = self.group_name
        # self.tv_device.save()
        # self.tv_device = self.get_tv_device(self.device_id)
        
        self.accept()
        
    


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        # self.tv_device.group_channel_name = self.group_name
        raw_image = text_data_json['data']['img']
        raw_image = base64.b64decode(raw_image)
        cec_hdmi_status = text_data_json['data']['hdmi_status']
        remote_last_image = ImageFile(io.BytesIO(raw_image), 'image.jpg')
        socket_status_updated = timezone.now()
        is_socket_connected = True
        # self.update_tv_device(self.device_id,cec_hdmi_status=cec_hdmi_status,remote_last_image=remote_last_image,socket_status_updated=socket_status_updated,is_socket_connected=is_socket_connected,)
        self.update_tv_device(self.device_id,{
            'cec_hdmi_status':cec_hdmi_status,
            'remote_last_image':remote_last_image,
            'socket_status_updated':socket_status_updated,
            'is_socket_connected':is_socket_connected,
            'group_channel_name':self.group_name,
        })
        
        #     self.tv_device.cec_hdmi_status = text_data_json['data']['hdmi_status']
            
        #     self.tv_device.remote_last_image = ImageFile(io.BytesIO(raw_image), 'image.jpg')
        #     self.tv_device.remote_last_image_updated = timezone.now()
        # self.tv_device.save()
        # print(self.tv_device.id, ' saved')
    
    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        socket_status_updated = timezone.now()
        is_socket_connected = False
        group_channel_name = None
        self.update_tv_device(self.device_id,{
            'socket_status_updated':socket_status_updated,
            'is_socket_connected':is_socket_connected,
            'group_channel_name':group_channel_name,
        })
        