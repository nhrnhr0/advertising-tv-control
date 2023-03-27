
from rest_framework import serializers
from tv.models import Broadcast
from core.models import Publisher

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name',)
        read_only_fields = ('id', 'name',)

class PublisherAssetsSerializer(serializers.ModelSerializer):
    def get_media_url(self, obj):
        return obj.media.url
    # publisher = PublisherSerializer(many=True)
    class Meta:
        model = Broadcast
        fields = ('id', 'name','updated','created','media','media_type', 'publisher')
        read_only_fields = ('id', 'name','updated','created','media','media_type', 'media_url', 'publisher')
    