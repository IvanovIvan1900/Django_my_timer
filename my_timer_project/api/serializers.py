from rest_framework import serializers

from main.models import TimeTrack

class TimeTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTrack
        fields = ['task', 'date_start', 'date_stop', 'duration_sec', 'is_active', 'user', 'id']
