from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Anyone can read. Only organizers (staff users) can create events.
    Only the event's own organizer (or a superuser) can edit/delete it."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user or request.user.is_superuser
