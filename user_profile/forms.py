from django import forms
from django.contrib.auth.models import User
from .models import Profile
from allauth.account.forms import SignupForm
from allauth.account.forms import SignupForm
from .models import WomenInTech, OS_Maintainer, Mentor


class UserUpdateForm(forms.ModelForm):
    """Form for updating user data"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating profile data"""

    class Meta:
        model = Profile
        fields = ["image"]


class CustomSignupForm(SignupForm):
    USER_TYPE_CHOICES = [
        ("wit", "Women in Tech"),
        ("osm", "Open Source Maintainer"),
        ("mentor", "Mentor"),
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, label="User Type")

    def save(self, request):
        user = super().save(request)
        user_type = self.cleaned_data.get("user_type")

        # Add user type to user object
        if user_type == "wit":
            WomenInTech.objects.create(user=user)
        elif user_type == "osm":
            OS_Maintainer.objects.create(user=user)
        elif user_type == "mentor":
            Mentor.objects.create(user=user)

        user.save()
        return user


class WomenInTechUpdateForm(forms.ModelForm):
    class Meta:
        model = WomenInTech
        fields = [
            "image",
            "tech_specialties",
            "years_of_experience",
            "github_username",
            "about",
        ]


class OS_MaintainerUpdateForm(forms.ModelForm):
    class Meta:
        model = OS_Maintainer
        fields = ["image", "github_username", "about"]


class MentorUpdateForm(forms.ModelForm):
    class Meta:
        model = Mentor
        fields = ["image", "expertise", "years_of_experience", "about"]
