import os
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Payment, ProjectFunding, WITFunding


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        if event.type == "payment_succeeded":
            payment_intent = event.data.object
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent.id
                )
                payment.status = "SUCCESS"
                payment.save()

                # Distribute funds to projects and WIT initiatives
                distribute_funds(payment)

            except Payment.DoesNotExist:
                print(f"Payment not found for PaymentIntent: {payment_intent.id}")

    except ValueError as e:
        return HttpResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_completed_checkout(session)

    return HttpResponse({"received": True})


def distribute_funds(payment):
    # Assuming you have a way to determine distribution amounts
    # This is a simplified example - implement your actual distribution logic
    project_amount = payment.amount * Decimal("0.7")  # 70% to projects
    wit_amount = payment.amount * Decimal("0.3")  # 30% to WIT

    # Create funding records
    ProjectFunding.objects.create(
        project=payment.project,  # Assuming you have a project assigned
        payment=payment,
        amount=project_amount,
    )

    WITFunding.objects.create(
        wit=payment.wit,  # Assuming you have a WIT assigned
        payment=payment,
        amount=wit_amount,
    )
