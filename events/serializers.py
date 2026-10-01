from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Event, Registration


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source="organizer.username")
    registered_count = serializers.IntegerField(read_only=True)
    seats_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "description", "location", "start_time", "end_time",
            "capacity", "organizer", "registered_count", "seats_left", "created_at",
        ]

    def validate(self, data):
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError("end_time must be after start_time.")
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    event_title = serializers.ReadOnlyField(source="event.title")

    class Meta:
        model = Registration
        fields = [
            "id", "user", "event", "event_title", "full_name", "email",
            "phone", "status", "created_at", "cancelled_at",
        ]
        read_only_fields = ["event", "status", "created_at", "cancelled_at"]


class RegistrationFormSerializer(serializers.ModelSerializer):
    """Registration form submission (POST /api/events/<id>/register/)."""

    class Meta:
        model = Registration
        fields = ["full_name", "email", "phone"]
