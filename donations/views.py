# donations/views.py
import json

import stripe
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from os_project.models import Project
from user_profile.models import WomenInTech

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
    amount = session.amount_total / 100  # Convert from cents

    # Create payment record
    payment = Payment(
        confirmation_number=session.id,
        user_id=metadata.get("user_id"),
        amount=amount,
        status="SUCCESS",
        stripe_payment_intent_id=session.payment_intent,
    )

    # Update project funding or add sponsorship details
    if payment_type == "project":
        project_id = metadata.get("project_id")
        if project_id:
            project = Project.objects.get(id=project_id)
            payment.project = project
            project.current_funding += amount
            project.save()

    elif payment_type == "sponsor":
        wit_id = metadata.get("wit_id")
        if wit_id:
            wit = WomenInTech.objects.get(id=wit_id)
            payment.sponsored_user = wit

    payment.save()


@csrf_exempt
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
                    project = Project.objects.get(id=session.metadata.get("project_id"))
                    payment.project = project
                    # Update project funding
                    project.current_funding += payment.amount
                    project.save()

                if session.metadata.get("wit_id"):
                    payment.sponsored_user = WomenInTech.objects.get(
                        id=session.metadata.get("wit_id")
                    )

            payment.save()

        return render(request, "donations/success.html", {"payment": payment})

    except Exception as e:
        return render(
            request,
            "donations/error.html",
            {"error_message": f"Error retrieving payment: {str(e)}"},
        )
