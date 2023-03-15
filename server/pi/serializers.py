from rest_framework import serializers

from .models import PiDevice
from core.models import TvOpeningHours

class PiDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PiDevice
        fields = "__all__"


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = TvOpeningHours
        fields = ('weekday','from_hour','to_hour',)