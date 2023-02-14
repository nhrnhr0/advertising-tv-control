import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import base64
from .models import PiDevice
from django.utils import timezone
import os
import io
from django.core.files.images import ImageFile

from django.conf import settings

open_socket_connections = {}
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        device_id = text_data_json.get('device', None)
        tv_device, created = PiDevice.objects.get_or_create(device_id=device_id)
        self.tv_device = tv_device
        print('got message from ', device_id)
        # tv_device.is_socket_connected = True
        tv_device.socket_status_updated = timezone.now()
        open_socket_connections[device_id] = self
        if(message_type == 'status'):
            raw_image = text_data_json['data']['img']
            raw_image = base64.b64decode(raw_image)
            
            tv_device.cec_hdmi_status = text_data_json['data']['hdmi_status']
            
            # settings.MEDIA_ROOT
            # img_url = 'static/media_root/last_images/' + str(tv_device.id) + '/image.png'
            # img_path = os.path.join(settings.MEDIA_ROOT, 'last_images', str(tv_device.id), 'image.png')
            # os.makedirs(os.path.dirname(img_path), exist_ok=True)
            # with open(img_path, 'wb') as f:
            #     f.write(raw_image)
            tv_device.remote_last_image = ImageFile(io.BytesIO(raw_image), 'image.jpg')
            tv_device.remote_last_image_updated = timezone.now()
            
            # tv_device.remote_status = text_data_json['data']['status']
            # tv_device.remote_status_updated = timezone.now()
            
        tv_device.save()
        print(tv_device.id, ' saved')
    
    def disconnect(self, code):
        self.tv_device.socket_status_updated = timezone.now()
        open_socket_connections.pop(self.tv_device.device_id, None)
        self.tv_device.save()
        return super().disconnect(code)