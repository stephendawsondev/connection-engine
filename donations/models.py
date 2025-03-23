import uuid
from decimal import Decimal
from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django_countries.fields import CountryField


# Create your models here.
class Payment(models.Model):
    project = models.ForeignKey(
        "os_project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    sponsored_user = models.ForeignKey(
        "user_profile.WomenInTech",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sponsorships",
    )
    confirmation_number = models.CharField(max_length=32, null=False, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    county = models.CharField(max_length=80, null=True, blank=True)
    country = CountryField(blank_label="Country *", null=True, blank=True)  # type: ignore[call-overload]
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("SUCCESS", "Success"), ("FAILED", "Failed"), ("PENDING", "Pending")],
        default="PENDING",
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=Decimal("0.00")
    )
    stripe_payment_intent_id = models.CharField(max_length=254, null=True, blank=True)

    def _generate_confirmation_number(self):
        """
        Generate a random, unique confirmation number using UUID.
        """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the confirmation number
        if it hasn't been set already.
        """
        if not self.confirmation_number:
            self.confirmation_number = self._generate_confirmation_number()

        # Update the grand total
        self.grand_total = self.amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.confirmation_number}"


class ProjectFunding(models.Model):
    project = models.ForeignKey("os_project.Project", on_delete=models.CASCADE)
    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class WITFunding(models.Model):
    wit = models.ForeignKey("user_profile.WomenInTech", on_delete=models.CASCADE)
    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
