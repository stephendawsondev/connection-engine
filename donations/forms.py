from django import forms

from .models import Payment, ProjectFunding, WITFunding


class PaymentForm(forms.ModelForm):
    TARGET_CHOICES = [
        ("project", "Project"),
        ("wit", "Women in Tech"),
    ]
    target = forms.ChoiceField(choices=TARGET_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Payment
        fields = [
            "full_name",
            "email",
            "phone_number",
            "street_address1",
            "street_address2",
            "postcode",
            "town_or_city",
            "county",
            "country",
            "target",
        ]


class ProjectFundingForm(forms.ModelForm):
    class Meta:
        model = ProjectFunding
        fields = ["amount"]


class WITFundingForm(forms.ModelForm):
    class Meta:
        model = WITFunding
        fields = ["wit", "amount"]


class WomenInTechSearchForm(forms.Form):
    search = forms.CharField(required=False)
    tech_specialties = forms.CharField(
        required=False, widget=forms.Select(attrs={"class": "select select-bordered"})
    )
    experience_level = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={"class": "select select-bordered"})
    )
