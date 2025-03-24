from decimal import Decimal

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Payment, ProjectFunding, WITFunding


@admin.register(Payment)
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
    actions = ["process_payment"]

    @admin.action(description="Process Selected Payments")
    def process_payment(self, request, queryset):
        for payment in queryset:
            if payment.status != "SUCCESS":
                try:
                    # Retrieve the session from Stripe
                    session = stripe.checkout.Session.retrieve(
                        payment.confirmation_number
                    )

                    # Update payment record from session data
                    payment.amount = Decimal(str(session.amount_total / 100))
                    payment.email = (
                        session.customer_details.email
                        if hasattr(session, "customer_details")
                        else request.user.email
                    )
                    payment.full_name = (
                        request.user.get_full_name() or request.user.username
                    )
                    payment.status = "SUCCESS"
                    payment.stripe_payment_intent_id = session.payment_intent

                    # Handle project and WIT data from metadata
                    if hasattr(session, "metadata"):
                        if session.metadata.get("project_id"):
                            project = Project.objects.get(
                                id=session.metadata.get("project_id")
                            )
                            payment.project = project
                            project.current_funding += payment.amount
                            project.save()
                        if session.metadata.get("wit_id"):
                            payment.sponsored_user = WomenInTech.objects.get(
                                id=session.metadata.get("wit_id")
                            )
                            payment.save()

                    payment.save()
                    self.message_user(
                        request,
                        f"Successfully processed payment {payment.confirmation_number}",
                        messages.SUCCESS,
                    )
                except Exception as e:
                    self.message_user(
                        request,
                        f"Error processing payment {payment.confirmation_number}: {str(e)}",
                        messages.ERROR,
                    )


@admin.register(ProjectFunding)
class ProjectFundingAdmin(admin.ModelAdmin):
    list_display = ("project", "payment", "amount", "created_at")
    ordering = ("-created_at",)
    actions = ["update_project_funding"]

    @admin.action(description="Update Project Funding")
    def update_project_funding(self, request, queryset):
        for funding in queryset:
            try:
                project = funding.project
                project.current_funding = sum(
                    pf.amount for pf in ProjectFunding.objects.filter(project=project)
                )
                project.save()
                self.message_user(
                    request,
                    f"Successfully updated funding for project {project.title}",
                    messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error updating funding for project {project.title}: {str(e)}",
                    messages.ERROR,
                )


@admin.register(WITFunding)
class WITFundingAdmin(admin.ModelAdmin):
    list_display = ("wit", "payment", "amount", "created_at")
    ordering = ("-created_at",)
    actions = ["update_wit_funding"]

    @admin.action(description="Update WIT Funding")
    def update_wit_funding(self, request, queryset):
        for funding in queryset:
            try:
                wit = funding.wit
                wit.total_funding = sum(
                    wf.amount for wf in WITFunding.objects.filter(wit=wit)
                )
                wit.save()
                self.message_user(
                    request,
                    f"Successfully updated funding for WIT {wit.user.username}",
                    messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error updating funding for WIT {wit.user.username}: {str(e)}",
                    messages.ERROR,
                )
