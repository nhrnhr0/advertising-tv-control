from tv.models import BroadcastInTvs, BroadcastInTvsSchedule
from rest_framework import serializers
class ScheduleSerializer(serializers.ModelSerializer):
    def get_content(self,obj):
        return obj.get_data()
    content = serializers.SerializerMethodField()
    is_active_now = serializers.SerializerMethodField()
    def get_is_active_now(self,obj):
        return obj.is_active()
    class Meta:
        model= BroadcastInTvsSchedule
        fields = ('id', 'content_type', 'content','is_active_now',)
    
class BroadcastInTvsDashboardSerializers(serializers.ModelSerializer):
    broadcast__name = serializers.CharField(source='broadcast.name', read_only=True)
    broadcast__media = serializers.SerializerMethodField()
    broadcast__media_type = serializers.CharField(source='broadcast.media_type', read_only=True)
    tvs_list = serializers.SerializerMethodField()
    activeSchedule = ScheduleSerializer()
    
    def get_broadcast__media(self, obj):
        return obj.broadcast.media.url

    def get_tvs_list(self, obj):
        # id and name of the tvs that the broadcast is in.
        return obj.tvs.all().values('id', 'name')
    # serializers.CharField(source='broadcast.media', read_only=True)
    class Meta:
        model = BroadcastInTvs
        fields = ('id','broadcast','broadcast__name', 'broadcast__media', 'broadcast__media_type','duration', 'order', 'updated', 'created','master','tvs_list', 'activeSchedule')
        
class BroadcastInTvsDetailDashboardSerializers(serializers.ModelSerializer):
    broadcast__name = serializers.CharField(source='broadcast.name', read_only=True)
    broadcast__media = serializers.SerializerMethodField()
    broadcast__media_type = serializers.CharField(source='broadcast.media_type', read_only=True)
    tvs_list = serializers.SerializerMethodField()
    activeSchedule = ScheduleSerializer()
    def get_tvs_list(self, obj):
        # id and name of the tvs that the broadcast is in.
        return obj.tvs.all().values('id', 'name')
    def get_broadcast__media(self, obj):
        return obj.broadcast.media.url
    class Meta:
        model = BroadcastInTvs
        fields = ('id', 'broadcast', 'broadcast__name', 'broadcast__media', 'broadcast__media_type',
                  'tvs','tvs_list', 'duration', 'order', 'updated', 'created','master','activeSchedule')
    
from core.models import TvOpeningHours
class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = TvOpeningHours
        fields = ('id', 'weekday','from_hour','to_hour',)
from tv.models import Tv
class DashboardTvsSerializer(serializers.ModelSerializer):
    opening_hours = OpeningHoursSerializer(many=True)
    class Meta:
        model = Tv
        fields = ('id', 'name', 'opening_hours')