from django.urls import path

from . import views

urlpatterns = [
    # paths goes here
    path("", views.donations, name="donations"),
    path("donations/process/", views.process_donation, name="process_donation"),
]
