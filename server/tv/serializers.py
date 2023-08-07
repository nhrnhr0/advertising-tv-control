

from rest_framework import routers, serializers, viewsets

from dashboard.ads_serialisers import OpeningHoursSerializer
from .models import Tv, Broadcast, BroadcastInTv, BroadcastInTvs
from django.db.models import Q
from django.conf import settings

class BroadcastInTvsSerializer(serializers.ModelSerializer):
    broadcast__name = serializers.CharField(source='broadcast.name', read_only=True)
    broadcast__media = serializers.SerializerMethodField()
    broadcast__media_type = serializers.CharField(source='broadcast.media_type', read_only=True)
    def get_broadcast__media(self, obj):
        return obj.broadcast.media.url
    class Meta:
        model = BroadcastInTvs
        fields = ('id', 'broadcast','broadcast__name', 'broadcast__media', 'broadcast__media_type', 'duration', 'order', 'created', 'master',)

class BroadcastInTvSerializer(serializers.ModelSerializer):
    broadcast__name = serializers.CharField(source='broadcast.name', read_only=True)
    broadcast__media = serializers.SerializerMethodField()
    broadcast__media_type = serializers.CharField(source='broadcast.media_type', read_only=True)
    def get_broadcast__media(self, obj):
        return obj.broadcast.media.url
    # serializers.CharField(source='broadcast.media', read_only=True)
    class Meta:
        model = BroadcastInTv
        fields = ('broadcast','broadcast__name', 'broadcast__media', 'broadcast__media_type','duration', 'order', 'updated', 'created','master')
        
class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = ('id', 'name', 'updated', 'created', 'media','duration')

def fill_with_master_broadcasts(master_broadcasts, ret, remaining_time, i):
    # knapsack problem to fill the remaining time with master broadcasts, broadcasts can be repeated but not one after the other.
    # we need to find the best combination of broadcasts that will fill the remaining time.
    if remaining_time == 0:
        return ret, remaining_time
    if master_broadcasts.count() == 0:
        return ret, remaining_time
    if i == len(master_broadcasts):
        return ret, remaining_time
    broadcast = master_broadcasts[i]
    rim1 = float('-inf')
    if broadcast.duration <= remaining_time:
        ret.append(broadcast)
        ret1,rim1 = fill_with_master_broadcasts(master_broadcasts, ret, remaining_time - broadcast.duration, i)
    else:
        ret2,rim2 = fill_with_master_broadcasts(master_broadcasts, ret, remaining_time, i+1)
        if rim1 > rim2:
            ret = ret1
            remaining_time = rim1
        else:
            ret = ret2
            remaining_time = rim2
    return ret, remaining_time




# old TvSerializer ret:
# {
# "id": 20,
# "name": "testing",
# "updated": "2023-07-27T09:30:00.377716+03:00",
# "created": "2023-07-26T15:12:32.444387+03:00",
# "get_absolute_url": "/tv/20",
# "opening_hours": [
# {
# "id": 144,
# "weekday": 5,
# "from_hour": "07:00:00",
# "to_hour": "09:00:00"
# },
# {
# "id": 145,
# "weekday": 5,
# "from_hour": "09:05:00",
# "to_hour": "09:10:00"
# },
# {
# "id": 146,
# "weekday": 5,
# "from_hour": "09:15:00",
# "to_hour": "09:18:00"
# },
# {
# "id": 147,
# "weekday": 5,
# "from_hour": "09:18:00",
# "to_hour": "09:22:00"
# },
# {
# "id": 148,
# "weekday": 5,
# "from_hour": "09:20:00",
# "to_hour": "09:25:00"
# },
# {
# "id": 149,
# "weekday": 5,
# "from_hour": "09:27:00",
# "to_hour": "09:29:00"
# },
# {
# "id": 150,
# "weekday": 5,
# "from_hour": "09:32:00",
# "to_hour": "09:35:00"
# }
# ],
# "is_opening_hours_active": false,
# "broadcasts": [
# {
# "id": 122,
# "broadcast": 46,
# "broadcast__name": "סידרה מקצועית למראה תלתלים (1).jpg",
# "broadcast__media": "/media/broadcasts/%D7%A1%D7%99%D7%93%D7%A8%D7%94_%D7%9E%D7%A7%D7%A6%D7%95%D7%A2%D7%99%D7%AA_%D7%9C%D7%9E%D7%A8%D7%90%D7%94_%D7%AA%D7%9C%D7%AA%D7%9C%D7%99%D7%9D_2.jpg",
# "broadcast__media_type": "image",
# "duration": 20,
# "order": 10,
# "created": "2023-06-08T00:21:49.771992+03:00",
# "master": true
# },
# {
# "id": 121,
# "broadcast": 45,
# "broadcast__name": "מעדני בשר גולייה.png",
# "broadcast__media": "/media/broadcasts/%D7%9E%D7%A2%D7%93%D7%A0%D7%99_%D7%91%D7%A9%D7%A8_%D7%92%D7%95%D7%9C%D7%99%D7%99%D7%94.png",
# "broadcast__media_type": "image",
# "duration": 20,
# "order": 10,
# "created": "2023-06-08T00:21:00.682913+03:00",
# "master": true
# }
# ]
# }
from django.db.models.query import QuerySet
from tv.models import Tv, Spot
import numpy as np

class SpotSerializer(serializers.ModelSerializer):
    def get_is_active(self, spot_obj):
        return spot_obj.is_active()
    
    def get_assets(self, spot_obj):
        return spot_obj.get_assets_serialize()
    
    def get_duration(self, spot_obj):
        return spot_obj.get_duration()
    
    is_active = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    class Meta:
        model = Spot
        fields = ('id','updated','created','is_active', 'is_filler', 'duration','assets')



class TvSerializer(serializers.ModelSerializer):

        
    
    broadcasts = serializers.SerializerMethodField()
    def get_broadcasts(self, tv_obj):
        pass
        # [{
        # "id": 122,
        # "broadcast": 46,
        # "broadcast__name": "סידרה מקצועית למראה תלתלים (1).jpg",
        # "broadcast__media": "/media/broadcasts/%D7%A1%D7%99%D7%93%D7%A8%D7%94_%D7%9E%D7%A7%D7%A6%D7%95%D7%A2%D7%99%D7%AA_%D7%9C%D7%9E%D7%A8%D7%90%D7%94_%D7%AA%D7%9C%D7%AA%D7%9C%D7%99%D7%9D_2.jpg",
        # "broadcast__media_type": "image",
        # "duration": 20,
        # "order": 10,
        # "created": "2023-06-08T00:21:49.771992+03:00",
        # "master": true
        # },
        # {
        # "id": 121,
        # "broadcast": 45,
        # "broadcast__name": "מעדני בשר גולייה.png",
        # "broadcast__media": "/media/broadcasts/%D7%9E%D7%A2%D7%93%D7%A0%D7%99_%D7%91%D7%A9%D7%A8_%D7%92%D7%95%D7%9C%D7%99%D7%99%D7%94.png",
        # "broadcast__media_type": "image",
        # "duration": 20,
        # "order": 10,
        # "created": "2023-06-08T00:21:00.682913+03:00",
        # "master": true
        # }]
        # active_spots = tv_obj.get_active_spots()
        
        
        # fillers = tv_obj.get_active_filler_spots()
        # lcm, spots_list = tv_obj.get_loop_without_fillers()
        # loop_time_in_secounds = lcm * 60
        # loop = tv_obj.fill_loop(spots_list, fillers, loop_time_in_secounds)
        loop = tv_obj.get_loop_with_fillers()
        
        data = SpotSerializer(loop, many=True).data
        return data
    


    opening_hours = OpeningHoursSerializer(many=True)
    
    def get_fotters(self, tv_obj):
        fotters = tv_obj.get_tv_fotters()
        ret = []
        for f in fotters:
            ret.append({
                'title': f.title,
                'image': f.image.url,
                'index': f.get_image_index(),
            })
        return ret
    fotters = serializers.SerializerMethodField()
    
    class Meta:
        model = Tv
        fields = ('id', 'name',  'updated', 'created','fotters', 'get_absolute_url','opening_hours','broadcasts',)
        # fields = '__all__'