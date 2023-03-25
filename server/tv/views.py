from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from .serializers import TvSerializer
from .models import Tv, Broadcast, BroadcastInTv, playedBroadcast
import json
# Create your views here.
def tv_view(request, id):
    tv_obj = Tv.objects.get(id=id)
    context = {
        'tv_obj': tv_obj,
    }
    return render(request, 'tv/view_tv.html', context)

def get_publisher_assets_as_tv_demo(request, id):
    broadcast = Broadcast.objects.get(id=id)
    # return response:
    # {
    # "broadcasts": [
    # {
    # "broadcast": 8,
    # "broadcast__name": "WhatsApp Image 2023-02-20 at 13.29.55.jpeg",
    # "broadcast__media": "/media/broadcasts/WhatsApp_Image_2023-02-20_at_13.29.55.jpeg",
    # "broadcast__media_type": "image",
    # "duration": 10,
    # "order": 10,
    # "updated": "2023-03-12T04:56:07.874958+02:00",
    # "created": "2023-02-21T18:33:40.991595+02:00"
    # },
    # }
    ret = {
        'broadcasts': []
    }
    ret['broadcasts'].append({
        "broadcast": broadcast.id,
        "broadcast__name": broadcast.name,
        "broadcast__media": broadcast.media.url,
        "broadcast__media_type": broadcast.media_type,
        "duration": 20,
        "order": 10,
        "updated": broadcast.updated,
        "created": broadcast.created
    })
    return JsonResponse(ret, safe=False)

def view_tv_api(request, id):
    # /tv/api/1/?inactive=true
    
    tv_obj = Tv.objects.get(id=id)
    inactive = request.GET.get('inactive') == 'true'
    serializer = TvSerializer(tv_obj,context={'include_inactive': inactive})
    info = serializer.data
    return JsonResponse(info, safe=False)
    pass


import datetime
@csrf_exempt
def save_broadcasts_played(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        broadcasts = data['broadcasts']
        last_broadcast_uuid = None
        
        uri_key = data.get('key')
        added = 0
        for broadcast in broadcasts:
            broadcast_id = broadcast['broadcast']
            tv_display_id = broadcast['tv_display']
            try:
                tv = Tv.objects.get(id=tv_display_id)
                
                str_time = broadcast['time'] # 2023-02-20T13:38:41.198Z
                uuid= broadcast['uuid']
                if str_time.endswith('Z'):
                    str_time = str_time[:-1]
                time = datetime.datetime.fromisoformat(str_time)
                # fit to israel time
                time = time + datetime.timedelta(hours=2)
                
                
                last_broadcast_uuid = uuid
                if playedBroadcast.objects.filter(uuid=uuid).exists():
                    continue
                if not tv.is_in_opening_hours(time):
                    continue
                try:
                    is_approved = tv.uri_key == uri_key
                    obj = playedBroadcast.objects.create(broadcast_id=broadcast_id, tv_id=tv_display_id, time=time, uuid=uuid,uri_key=uri_key, is_approved=is_approved)
                    last_broadcast = obj
                    added += 1
                    broadcast_in_tv = BroadcastInTv.objects.get(broadcast_id=broadcast_id, tv_id=tv_display_id)
                    if is_approved:
                        if broadcast_in_tv.enable_countdown:
                            broadcast_in_tv.plays_left -= 1
                            if broadcast_in_tv.plays_left <= 0:
                                # broadcast_in_tv.plays_left = 0
                                broadcast_in_tv.is_active = False
                        if broadcast_in_tv.need_to_send_telegram_notification():
                            broadcast_in_tv.send_telegram_notification()
                        
                        broadcast_in_tv.save()
                except Exception as e:
                    print(e)
                    pass
            except Exception as e:
                print(e)
                pass
        print('adding broadcasts', len(broadcasts), 'added', added)
    # if last_broadcast:
    #     uid = last_broadcast.uuid
    # else:
    #     uid = None
        return JsonResponse({'success':True, 'last_uuid_played':last_broadcast_uuid}, safe=False)
    return JsonResponse({'success':False, 
                         'error':'only POST is allowed'}, safe=False)