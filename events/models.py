from django.conf import settings
from django.db import models


class Event(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organized_events"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        return self.registrations.filter(status=Registration.REGISTERED).count()

    @property
    def seats_left(self):
        return max(self.capacity - self.registered_count, 0)


class Registration(models.Model):
    REGISTERED = "registered"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [(REGISTERED, "Registered"), (CANCELLED, "Cancelled")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=REGISTERED)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "event"], name="unique_user_event_registration")
        ]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
