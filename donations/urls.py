from django.urls import path

from . import views

urlpatterns = [
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("success/", views.success, name="success"),
    # Sponsorship URLs
    path(
        "sponsorship/create-checkout-session/",
        views.create_sponsorship_session,
        name="create_sponsorship_session",
    ),
    # women in tech
    path(
        "sponsorship/", views.WomenInTechListView.as_view(), name="women_in_tech_list"
    ),
]
