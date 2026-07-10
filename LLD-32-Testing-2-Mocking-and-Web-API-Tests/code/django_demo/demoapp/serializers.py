from rest_framework import serializers
from demoapp.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "owner"]
        read_only_fields = ["owner"]      # the view sets the owner, not the client
