from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from pi.models import PiDevice
from django.core.files.images import ImageFile
import base64
import io
from datetime import datetime
# Create your views here.
@csrf_exempt
def pi_screenshot_view(request, pi_key):
    if request.method == 'POST':
        time = request.POST.get('time')
        image = request.POST.get('image')
        hdmi_status = request.POST.get('hdmi_status')
        time = datetime.fromtimestamp(int(float(time)))
        # get the object
        obj, created = PiDevice.objects.get_or_create(device_id=pi_key)
        obj.cec_hdmi_status = hdmi_status
        
        
        
        # convert base64 to image
        if obj.is_approved:
            # save image
            img = base64.b64decode(image)
            if img:
                image_file = ImageFile(io.BytesIO(img), 'image.jpg')
                if obj.remote_last_image:
                    obj.remote_last_image.delete()
                obj.remote_last_image = image_file
                obj.image_updated = time
        obj.socket_status_updated = time
        obj.telegram_connection_error_sent = False # reset the error
        obj.save()
        return HttpResponse('ok')
    return HttpResponse('ok2')

from tv.models import BroadcastInTv
from server.telegram_bot_interface import send_admin_message,edit_message_reply_markup
@csrf_exempt
def telegram_webhook_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('===================== TELEGRAM MESSAGE =====================\n',data, '\n============================================================')
        # if the message is a callback_query:
        if 'callback_query' in data:
            callback_query = data['callback_query']
            callback_data = callback_query['data']
            callback_data = json.loads(callback_data)
            action = callback_data['action']
            if action == 'notification_half':
                # get the broadcast
                broadcast_in_tv_id = callback_data['id']
                # get the broadcast
                b_in_tv = BroadcastInTv.objects.get(id=broadcast_in_tv_id)
                b_in_tv.telegram_notification_in = int((b_in_tv.plays_left or 1) / 2)
                b_in_tv.telegram_notification_sent = False
                b_in_tv.save()
            elif action == 'notification_0':
                # get the broadcast
                broadcast_in_tv_id = callback_data['id']
                # get the broadcast
                b_in_tv = BroadcastInTv.objects.get(id=broadcast_in_tv_id)
                b_in_tv.telegram_notification_in = 0
                b_in_tv.telegram_notification_sent = False
                b_in_tv.save()
            # remove keyboard from message
            edit_message_reply_markup(message_id=callback_query['message']['message_id'])
            
            replay_to = callback_query['message']['message_id']
            message = 'נזכיר לך בעוד <b>{}</b> שידורים'.format(int(b_in_tv.plays_left - b_in_tv.telegram_notification_in))
            send_admin_message(message, reply_to_message_id=replay_to)
    return HttpResponse('ok')