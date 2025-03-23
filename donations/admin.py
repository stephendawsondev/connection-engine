from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Payment, ProjectFunding, WITFunding


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = (
        "confirmation_number",
        "created_at",
        "grand_total",
        "stripe_payment_intent_id",
    )
    fields = (
        "confirmation_number",
        "user",
        "amount",
        "full_name",
        "email",
        "phone_number",
        "street_address1",
        "street_address2",
        "postcode",
        "town_or_city",
        "county",
        "country",
        "created_at",
        "status",
        "grand_total",
        "stripe_payment_intent_id",
    )
    list_display = (
        "confirmation_number",
        "created_at",
        "full_name",
        "grand_total",
    )
    ordering = ("-created_at",)


class ProjectFundingAdmin(admin.ModelAdmin):
    list_display = ("project", "payment", "amount", "created_at")
    ordering = ("-created_at",)


class WITFundingAdmin(admin.ModelAdmin):
    list_display = ("wit", "payment", "amount", "created_at")
    ordering = ("-created_at",)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(ProjectFunding, ProjectFundingAdmin)
admin.site.register(WITFunding, WITFundingAdmin)
