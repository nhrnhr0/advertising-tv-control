
from rest_framework import serializers
from tv.models import Broadcast
from core.models import Publisher

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name',)
        read_only_fields = ('id', 'name',)

class PublisherAssetsSerializer(serializers.ModelSerializer):
    publisher__name = serializers.SerializerMethodField()
    # def get_media_url(self, obj):
    #     return obj.media.url
    # publisher = PublisherSerializer(many=True)
    def get_publisher__name(self, obj):
        return obj.publisher.name
    
    class Meta:
        model = Broadcast
        fields = ('id', 'name','updated','created','media','media_type', 'publisher','publisher__name',)
        read_only_fields = ('id', 'name','updated','created','media','media_type', 'media_url', 'publisher', 'publisher__name',)
    