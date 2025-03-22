import json
import os

import stripe
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import PaymentForm, ProjectFundingForm, WITFundingForm
from .models import Payment, ProjectFunding, WITFunding

stripe.api_key = settings.STRIPE_SECRET_KEY


def donations(request):
    return render(request, "donations/donations.html")


@require_POST
def process_donation(request):
    try:
        data = json.loads(request.body)
        amount = int(float(data["amount"]) * 100)

        if amount <= 0:
            return JsonResponse({"error": "Amount must be positive"}, status=400)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="gbp",
            automatic_payment_methods={"enabled": True},
            metadata={
                "target": data.get("target", "project"),
                "amount": data["amount"],
                "save_info": data.get("save_info", "False"),
                "username": request.user.username,
            },
        )
        return JsonResponse({"clientSecret": intent["client_secret"]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
