from django.contrib import admin

from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ["created_at", "cancelled_at"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "organizer", "location", "start_time", "capacity", "registered_count"]
    list_filter = ["start_time", "organizer"]
    search_fields = ["title", "location"]
    inlines = [RegistrationInline]

    def save_model(self, request, obj, form, change):
        if not change and not obj.organizer_id:
            obj.organizer = request.user
        super().save_model(request, obj, form, change)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["user", "event", "full_name", "status", "created_at"]
    list_filter = ["status", "event"]
    search_fields = ["full_name", "email", "user__username"]
