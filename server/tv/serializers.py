

from rest_framework import routers, serializers, viewsets
from .models import Tv, Broadcast, BroadcastInTv
from django.db.models import Q


class BroadcastInTvSerializer(serializers.ModelSerializer):
    broadcast__name = serializers.CharField(source='broadcast.name', read_only=True)
    broadcast__media = serializers.SerializerMethodField()
    broadcast__media_type = serializers.CharField(source='broadcast.media_type', read_only=True)
    def get_broadcast__media(self, obj):
        return obj.broadcast.media.url
    # serializers.CharField(source='broadcast.media', read_only=True)
    class Meta:
        model = BroadcastInTv
        fields = ('broadcast','broadcast__name', 'broadcast__media', 'broadcast__media_type','duration', 'order', 'updated', 'created',)
        
class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = ('id', 'name', 'updated', 'created', 'media','duration')


class TvSerializer(serializers.ModelSerializer):
    
    broadcasts = serializers.SerializerMethodField()
    def get_broadcasts(self, obj):
        qset = BroadcastInTv.objects.select_related('tv', 'broadcast').filter(Q(tv=obj) and Q(active=True) and ~Q(broadcast__media_type='unknown')).order_by('order')
        # 
        serializer = BroadcastInTvSerializer(qset, many=True)
        return serializer.data
    class Meta:
        model = Tv
        fields = ('id', 'name',  'updated', 'created', 'get_absolute_url','broadcasts',)
        # fields = '__all__'