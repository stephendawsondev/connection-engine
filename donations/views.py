# donations/views.py
import json
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from os_project.models import Project
from user_profile.models import WomenInTech

from .forms import WomenInTechSearchForm
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_checkout_session(request):
    data = json.loads(request.body)
    amount = int(float(data.get("amount", 10)) * 100)  # Convert to cents
    type = data.get("type")
    id = data.get("id")
    success_url = (
        request.build_absolute_uri("/donations/success/")
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri("/donations/cancel/")

    metadata = {"user_id": request.user.id, "payment_type": type}

    product_name = "Donation"

    if type == "project":
        project = get_object_or_404(Project, id=id)
        metadata["project_id"] = project.id
        product_name = f"Donation to {project.title}"

    elif type == "sponsor":
        wit = get_object_or_404(WomenInTech, id=id)
        metadata["wit_id"] = wit.id
        product_name = f"Sponsorship for {wit.user.username}"

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )
        return JsonResponse({"id": checkout_session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_completed_checkout(session)

    return JsonResponse({"status": "success"})


def handle_completed_checkout(session):
    metadata = session.metadata
    payment_type = metadata.get("payment_type")
    user_id = metadata.get("user_id")
    amount = Decimal(str(session.amount_total / 100))  # Convert from cents

    # Create payment record
    payment = Payment(
        confirmation_number=session.id,
        user_id=user_id,
        amount=amount,
        status="SUCCESS",
        stripe_payment_intent_id=session.payment_intent,
    )

    # Update project funding or add sponsorship details
    if payment_type == "project":
        project_id = metadata.get("project_id")
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                payment.project = project
                payment.save()

                # Update the project funding
                project.update_funding()

            except Project.DoesNotExist:
                # Handle case where project doesn't exist
                payment.save()
        else:
            payment.save()

    elif payment_type == "sponsor":
        wit_id = metadata.get("wit_id")
        if wit_id:
            try:
                wit = WomenInTech.objects.get(id=wit_id)
                payment.sponsored_user = wit
                payment.save()
            except WomenInTech.DoesNotExist:
                payment.save()
        else:
            payment.save()
    else:
        payment.save()


# donations/views.py - update the success function


def success(request):
    """
    Handle successful payments
    """
    # Get the session ID from query parameters
    session_id = request.GET.get("session_id")
    if not session_id:
        return render(
            request, "donations/error.html", {"error_message": "No session ID provided"}
        )

    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        # Look for an existing payment or create one
        try:
            payment = Payment.objects.get(confirmation_number=session_id)
        except Payment.DoesNotExist:
            # Create payment record from session data
            payment = Payment(
                confirmation_number=session_id,
                user_id=request.user.id,
                amount=Decimal(str(session.amount_total / 100)),  # Convert from cents
                email=(
                    session.customer_details.email
                    if hasattr(session, "customer_details")
                    else request.user.email
                ),
                full_name=request.user.get_full_name() or request.user.username,
                status="SUCCESS",
                stripe_payment_intent_id=session.payment_intent,
            )
            # Handle project and WIT data from metadata
            if hasattr(session, "metadata"):
                if session.metadata.get("project_id"):
                    try:
                        project = Project.objects.get(
                            id=session.metadata.get("project_id")
                        )
                        payment.project = project
                        project.update_funding()
                        payment.save()
                    except Project.DoesNotExist:
                        payment.save()
                elif session.metadata.get("wit_id"):
                    try:
                        payment.sponsored_user = WomenInTech.objects.get(
                            id=session.metadata.get("wit_id")
                        )
                        payment.save()
                    except WomenInTech.DoesNotExist:
                        payment.save()
            else:
                payment.save()

        # Get project information if applicable
        project = payment.project
        if project:
            remaining_funding = project.funding_goal - project.current_funding
            funding_progress = project.funding_percentage()

            # Add recent payments to the context
            recent_payments = Payment.objects.exclude(status="PENDING").order_by(
                "-created_at"
            )[:5]

            return render(
                request,
                "donations/success.html",
                {
                    "payment": payment,
                    "project": project,
                    "remaining_funding": remaining_funding,
                    "funding_progress": funding_progress,
                    "recent_payments": recent_payments,  # Add this line
                    "save_info": request.session.get("save_info"),
                },
            )

            return render(
                request,
                "donations/success.html",
                {
                    "payment": payment,
                    "project": project,
                    "remaining_funding": remaining_funding,
                    "funding_progress": funding_progress,
                    "save_info": request.session.get("save_info"),
                },
            )
        else:
            return render(
                request,
                "donations/success.html",
                {"payment": payment, "save_info": request.session.get("save_info")},
            )
    except Exception as e:
        return render(
            request,
            "donations/error.html",
            {"error_message": f"Error retrieving payment: {str(e)}"},
        )


# Women iIn Tech List
class WomenInTechListView(ListView):
    model = WomenInTech
    template_name = "donations/sponsorship.html"
    context_object_name = "women_in_tech"
    paginate_by = 12

    def get_queryset(self):
        queryset = WomenInTech.objects.all()
        form = WomenInTechSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get("search")
            tech_specialties = form.cleaned_data.get("tech_specialties")
            experience_level = form.cleaned_data.get("experience_level")

            if search:
                queryset = queryset.filter(
                    Q(user__username__icontains=search)
                    | Q(tech_specialties__icontains=search)
                    | Q(user__first_name__icontains=search)
                    | Q(user__last_name__icontains=search)
                )

            if tech_specialties:
                queryset = queryset.filter(specialties=tech_specialties)

            if experience_level:
                queryset = queryset.filter(experience_level=experience_level)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = WomenInTechSearchForm(self.request.GET)
        return context


@csrf_exempt
def create_sponsorship_session(request):
    data = json.loads(request.body)
    amount = int(float(data.get("amount", 10)) * 100)  # Convert to cents
    wit_id = data.get("wit_id")
    success_url = request.build_absolute_uri("/donations/sponsorship/success/")
    cancel_url = request.build_absolute_uri("/donations/cancel/")

    try:
        wit = WomenInTech.objects.get(id=wit_id)
        product_name = f"Sponsorship for {wit.user.username}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": product_name,
                        },
                    },
                    "quantity": 1,
                    "amount": amount,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": request.user.id,
                "payment_type": "sponsor",
                "wit_id": wit_id,
            },
        )
        return JsonResponse({"id": checkout_session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def sponsorship_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return render(
            request, "donations/error.html", {"error_message": "No session ID provided"}
        )

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment = handle_completed_checkout(session)

        return render(
            request,
            "donations/sponsorship_success.html",
            {
                "payment": payment,
                "save_info": request.session.get("save_info"),
            },
        )
    except Exception as e:
        return render(
            request,
            "donations/error.html",
            {"error_message": f"Error retrieving payment: {str(e)}"},
        )
