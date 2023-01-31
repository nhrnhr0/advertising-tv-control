

from rest_framework import routers, serializers, viewsets
from .models import Tv, Broadcast, BroadcastInTv
class BroadcastInTvSerializer(serializers.ModelSerializer):
    broadcast__name = serializers.CharField(source='broadcast.name', read_only=True)
    broadcast__media = serializers.CharField(source='broadcast.media', read_only=True)
    class Meta:
        model = BroadcastInTv
        fields = ('broadcast','broadcast__name', 'broadcast__media', 'duration', 'order', 'updated', 'created',)
        
class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = ('id', 'name', 'updated', 'created', 'media','duration')
class TvSerializer(serializers.ModelSerializer):
    
    broadcasts = serializers.SerializerMethodField()
    def get_broadcasts(self, obj):
        qset = BroadcastInTv.objects.filter(tv=obj)
        serializer = BroadcastInTvSerializer(qset, many=True)
        return serializer.data
    class Meta:
        model = Tv
        fields = ('id', 'name',  'updated', 'created', 'get_absolute_url','broadcasts',)
        # fields = '__all__'