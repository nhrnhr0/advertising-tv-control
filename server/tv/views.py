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


def view_tv_api(request, id):
    tv_obj = Tv.objects.get(id=id)
    serializer = TvSerializer(tv_obj)
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
                        broadcast_in_tv.plays_left -= 1
                        if broadcast_in_tv.plays_left <= 0:
                            # broadcast_in_tv.plays_left = 0
                            broadcast_in_tv.is_active = False

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