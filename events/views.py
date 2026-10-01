from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import Event, Registration
from .permissions import IsOrganizerOrReadOnly
from .serializers import (
    EventSerializer, RegistrationFormSerializer, RegistrationSerializer, SignupSerializer,
)


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


class EventListCreateView(generics.ListCreateAPIView):
    """GET: list all events (public). POST: create event (organizer only)."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: event details (public). PUT/PATCH/DELETE: owner organizer only."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]


class EventRegisterView(APIView):
    """POST: submit the registration form for an event (logged-in users)."""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        event = get_object_or_404(Event.objects.select_for_update(), pk=pk)
        form = RegistrationFormSerializer(data=request.data)
        form.is_valid(raise_exception=True)

        if event.end_time < timezone.now():
            return Response({"detail": "This event has already ended."}, status=400)

        existing = Registration.objects.filter(user=request.user, event=event).first()
        if existing and existing.status == Registration.REGISTERED:
            return Response({"detail": "You are already registered for this event."}, status=400)
        if event.seats_left <= 0:
            return Response({"detail": "Event is full."}, status=400)

        if existing:  # re-register after cancelling
            for field, value in form.validated_data.items():
                setattr(existing, field, value)
            existing.status = Registration.REGISTERED
            existing.cancelled_at = None
            existing.save()
            registration = existing
        else:
            registration = Registration.objects.create(
                user=request.user, event=event, **form.validated_data
            )
        return Response(RegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)


class MyRegistrationsView(generics.ListAPIView):
    """GET: list the logged-in user's registrations."""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user).select_related("event")


class RegistrationDetailView(generics.RetrieveAPIView):
    """GET: view one of my registrations."""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)


class CancelRegistrationView(APIView):
    """POST or DELETE: cancel my registration."""
    permission_classes = [permissions.IsAuthenticated]

    def _cancel(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk, user=request.user)
        if reg.status == Registration.CANCELLED:
            return Response({"detail": "Already cancelled."}, status=400)
        reg.status = Registration.CANCELLED
        reg.cancelled_at = timezone.now()
        reg.save()
        return Response({"detail": "Registration cancelled."})

    def post(self, request, pk):
        return self._cancel(request, pk)

    def delete(self, request, pk):
        return self._cancel(request, pk)


class EventRegistrationsView(generics.ListAPIView):
    """GET: an organizer sees who registered for THEIR event."""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        user = self.request.user
        if event.organizer != user and not user.is_superuser:
            self.permission_denied(self.request, message="Only the organizer can view this.")
        return event.registrations.select_related("user")


class ApiRootView(APIView):
    """GET /api/ : list of main endpoints."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "signup": reverse("signup", request=request),
            "login": reverse("login", request=request),
            "me": reverse("me", request=request),
            "events": reverse("event-list", request=request),
            "my_registrations": reverse("my-registrations", request=request),
        })


class MeView(APIView):
    """GET: info about the logged-in user (used by the web UI)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.id, "username": u.username, "email": u.email,
            "is_staff": u.is_staff, "is_superuser": u.is_superuser,
        })
