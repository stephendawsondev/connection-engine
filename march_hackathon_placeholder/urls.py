from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views

handler404 = "march_hackathon_placeholder.views.custom_page_not_found"
handler500 = "march_hackathon_placeholder.views.custom_server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("profile/", include("user_profile.urls")),
    path("projects/", include("os_project.urls")),
    path("donations/", include("donations.urls")),
    path("", include("home.urls")),
]
