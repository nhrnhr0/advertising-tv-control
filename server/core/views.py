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
        obj.save()
        return HttpResponse('ok')
    return HttpResponse('ok2')