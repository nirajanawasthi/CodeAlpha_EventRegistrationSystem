from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="events/index.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("events.urls")),
]
