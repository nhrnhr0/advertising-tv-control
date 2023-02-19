import base64
import io
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.core.files.images import ImageFile
from django.utils import timezone

from .models import PiDevice
from .serializers import PiDeviceSerializer



# open_socket_connections = {}

def send_reboot_to_channel(channel_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        "type": "do_reboot",
    })
    
def send_hdmi_cec_off_to_channel(channel_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        "type": "do_hdmi_cec_off",
    })
    
def send_hdmi_cec_on_to_channel(channel_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        "type": "do_hdmi_cec_on",
    })
    
def send_relaunch_kiosk_browser_to_channel(channel_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        "type": "do_relaunch_kiosk_browser",
    })

class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        """
        added the intial which enables me to access this from all function like where
         i need it on the update_tv_device
        """
        super().__init__(args, kwargs)
        # The uuid
        self.chat_room = None
        # The device id in string format same a chat room
        self.device_id = None
        # the pi_device instance
        self.pi_device = None
        # the chat room
        self.group_channel_name = None

    def do_reboot(self, event):
        print('rebooting')
        self.send(text_data=json.dumps({
            'type': 'command',
            'command': 'reboot'
        }))
        
    def do_hdmi_cec_off(self, event):
        print('hdmi_cec_off')
        self.send(text_data=json.dumps({
            'type': 'command',
            'command': 'hdmi_cec_off'
        }))
        pass
    def do_hdmi_cec_on(self, event):
        print('hdmi_cec_on')
        self.send(text_data=json.dumps({
            'type': 'command',
            'command': 'hdmi_cec_on'
        }))
        pass
    def do_relaunch_kiosk_browser(self, event):
        print('relaunch_kiosk_browser')
        self.send(text_data=json.dumps({
            'type': 'command',
            'command': 'relaunch_kiosk_browser'
        }))
        pass

    def update_tv_device(self, device_id, args_dict):
        """
        This is used to create or update the PIDevice base on  existence
        """
        tv_device, created = PiDevice.objects.get_or_create(device_id=device_id)
        if args_dict:
            for key, value in args_dict.items():
                print("the keys", key, "and value", value)
                setattr(tv_device, key, value)
            tv_device.save()
        # set the value
        self.pi_device = tv_device
        print(tv_device.id, ' saved')

    def connect(self):
        """
        the connect requires just
        """
        self.chat_room = self.scope['url_route']['kwargs']['uid']
        # if the device id is not passed I disconnect the connection
        if not self.chat_room:
            self.disconnect(code=1014)
        self.device_id = str(self.chat_room)
        self.group_channel_name = 'chat_%s' % self.device_id

        async_to_sync(self.channel_layer.group_add)(
            self.group_channel_name,
            self.channel_name
        )
        socket_status_updated = timezone.now()
        is_socket_connected = True
        self.update_tv_device(self.device_id,
                              {'group_channel_name': self.group_channel_name,
                               'socket_status_updated': socket_status_updated,
                               'is_socket_connected': is_socket_connected})

        self.accept()

    def receive(self, text_data):
        """
        this receives the json format and sends a json response in a serialized format for now to enable the user
        see what's going on
        """
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        # fixme: uncomment this and remove line 14
        raw_image = text_data_json['data']['img']
        raw_image = base64.b64decode(raw_image)

        cec_hdmi_status = text_data_json['data']['hdmi_status']
        remote_last_image = ImageFile(io.BytesIO(raw_image), 'image.jpg')
        socket_status_updated = timezone.now()
        is_socket_connected = True

        #  we don't need to await it because we are using WebsocketConsumer not the async
        self.update_tv_device(self.device_id, {
            'cec_hdmi_status': cec_hdmi_status,
            'remote_last_image': remote_last_image,
            'socket_status_updated': socket_status_updated,
            'is_socket_connected': is_socket_connected,
            'group_channel_name': self.group_channel_name
        })

        # Fixme: You can remove this i added it for testing
        # send a response to the user about the socket connection
        # show list of online users
        # self.send(text_data=json.dumps({
        #     "type": "connected",
        #     "data": PiDeviceSerializer(instance=self.pi_device).data,
        # }))

    def disconnect(self, code):
        """
        this is used to disconnect the websocket with the status code
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.group_channel_name,
            self.channel_name
        )
        socket_status_updated = timezone.now()
        is_socket_connected = False
        group_channel_name = None
        self.update_tv_device(self.device_id, {
            'socket_status_updated': socket_status_updated,
            'is_socket_connected': is_socket_connected,
            'group_channel_name': group_channel_name,
        })
        return super().disconnect(code)
