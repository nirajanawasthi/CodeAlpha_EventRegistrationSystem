from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("", views.ApiRootView.as_view(), name="api-root"),
    # auth
    path("auth/signup/", views.SignupView.as_view(), name="signup"),
    path("auth/login/", obtain_auth_token, name="login"),  # returns {"token": "..."}

    path("auth/me/", views.MeView.as_view(), name="me"),

    # events
    path("events/", views.EventListCreateView.as_view(), name="event-list"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path("events/<int:pk>/register/", views.EventRegisterView.as_view(), name="event-register"),
    path("events/<int:pk>/registrations/", views.EventRegistrationsView.as_view(), name="event-registrations"),

    # my registrations (view / cancel)
    path("registrations/", views.MyRegistrationsView.as_view(), name="my-registrations"),
    path("registrations/<int:pk>/", views.RegistrationDetailView.as_view(), name="registration-detail"),
    path("registrations/<int:pk>/cancel/", views.CancelRegistrationView.as_view(), name="registration-cancel"),
]
