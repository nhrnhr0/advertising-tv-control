

from rest_framework import routers, serializers, viewsets
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


class TvSerializer(serializers.ModelSerializer):
    def merge_masters_and_publishers(publishers, masters):
        # we have a list of publishers and masters broadcasts, the 2 together should be 10 minutes.
        # we need to put the publishers equaly spaced in the 10 minutes (in the masters broadcasts).
        
        # first we need to devide the length of the masters broadcasts to the length of the publishers broadcasts.
        # this will give us the number of masters broadcasts that we need to put between each publisher broadcast.
        # we need to put the masters broadcasts in the middle of the publishers broadcasts.
        if len(publishers) == 0:
            return masters
        num_of_masters = len(masters) // len(publishers) 
        #  // is the integer division operator. (5//2 = 2)

        ret = []
        i = 0
        for publisher in publishers:
            ret.append(publisher)
            for j in range(num_of_masters):
                ret.append(masters[i])
                i += 1
        return ret
        
    
    broadcasts = serializers.SerializerMethodField()
    def get_broadcasts(self, tv_obj):
        # old code
        # qset = BroadcastInTv.objects.select_related('tv', 'broadcast')
        # qset = qset.filter(tv=obj)
        # qset= qset.filter(active=True)
        # qset = qset.filter(~Q(broadcast__media_type='unknown'))
        # qset = qset.filter(plays_left__gt=0)
        # qset = qset.order_by('order')
        
        # instructions:
        # we need to return a list of broadcasts of duration 10 minutes.
        # broadcasts that are not active should not be returned at all.
        # broadcasts that are active but have no plays left should not be returned as well.
        # the media type of the broadcast should be known. (~Q(broadcast__media_type='unknown'))
        # first we pick all broadcasts that are active and have plays left and are not master broadcasts, those need to appear one time only.
        # then we pick all broadcasts that are active and have plays left and are master broadcasts, those need to appear as many times to fill the 10 minutes.

        # new code:
        queryset = BroadcastInTvs.objects.select_related('broadcast').prefetch_related('tvs',)
        queryset = queryset.filter(tvs=tv_obj)
        # include_inactive = self.context.get("include_inactive", False)
        # if we need to show also hidden broadcasts, it's only demo to check the assests.
        # if not include_inactive:
            # queryset = queryset.filter(active=True)
            # queryset = queryset.filter(Q(plays_left__gt=0) & Q(enable_countdown=True))
            # queryset = queryset.filter(Q(plays_left__gt=0) | Q(enable_countdown=False))
        # filter only activeSchedule exists and activeSchedule.is_active = True
        queryset = queryset.filter(activeSchedule__isnull=False)
        queryset = queryset.filter(activeSchedule__is_active_var=True)
        queryset = queryset.filter(~Q(broadcast__media_type='unknown'))
        
        master_broadcasts = queryset.filter(master=True)
        publishers_broadcasts = queryset.filter(master=False)
        
        # first we pick all broadcasts that are active and have plays left and are not master broadcasts, those need to appear one time only.
        ret = []
        ret_publishers_broadcasts = []
        ret_masters_broadcasts = []
        total_duration = 0
        
        for broadcast in publishers_broadcasts:
            # ret.append(broadcast)
            ret_publishers_broadcasts.append(broadcast)
            total_duration += broadcast.duration
            if total_duration >= settings.MAX_PLAYLIST_DURATION:
                break
        
        i= 0
        if len(master_broadcasts) != 0:
            while total_duration < settings.MAX_PLAYLIST_DURATION:
                broadcast = master_broadcasts[i % len(master_broadcasts)]
                if total_duration + broadcast.duration > settings.MAX_PLAYLIST_DURATION:
                    # we need to checked if there is a that is fitting in the remaining time or smaller.
                    # if there is no broadcast that fits we need to break the loop.
                    # if there is a broadcast that fits we need to add it and break the loop.
                    for broadcast in master_broadcasts:
                        if total_duration + broadcast.duration == settings.MAX_PLAYLIST_DURATION:
                            ret_masters_broadcasts.append(broadcast)
                            total_duration += broadcast.duration
                            break
                    
                ret_masters_broadcasts.append(broadcast)
                total_duration += broadcast.duration
                i += 1
            i=0
            if total_duration > settings.MAX_PLAYLIST_DURATION:
                ret_masters_broadcasts.pop()
                total_duration -= broadcast.duration
                res1, remaining = fill_with_master_broadcasts(master_broadcasts, ret_masters_broadcasts, settings.MAX_PLAYLIST_DURATION - total_duration, i)
                if remaining != 0:
                    ret_masters_broadcasts.pop()
                    total_duration -= broadcast.duration
                    res1, remaining = fill_with_master_broadcasts(master_broadcasts, ret_masters_broadcasts, settings.MAX_PLAYLIST_DURATION - total_duration, i)
                ret_masters_broadcasts = res1
        
        
        merge_broadcasts = TvSerializer.merge_masters_and_publishers(ret_publishers_broadcasts, ret_masters_broadcasts)
        

        serializer = BroadcastInTvsSerializer(merge_broadcasts, many=True)
        return serializer.data
    class Meta:
        model = Tv
        fields = ('id', 'name',  'updated', 'created', 'get_absolute_url','is_opening_hours_active','broadcasts',)
        # fields = '__all__'