from django import forms

# Subject choices
SUBJECT_CHOICES = [
    ("general", "General Inquiry"),
    ("tech", "Technical Support"),
    ("partnership", "Partnerships"),
    ("sponsorship", "Sponsorship"),
    ("other", "Other"),
]


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "Your Name"}
        ),
        label="Name",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "Your Email"}
        ),
        label="Email",
    )
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
        label="Subject",
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 5,
                "placeholder": "Your Message",
            }
        ),
        label="Message",
    )
