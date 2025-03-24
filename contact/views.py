from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import ContactForm


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject_value = form.cleaned_data["subject"]
            message_body = form.cleaned_data["message"]

            # Get the label of the selected subject
            subject_label = dict(form.fields["subject"].choices).get(
                subject_value, subject_value
            )

            email_subject = f"Connection Engine: {subject_label}"
            email_message = (
                f"Name: {name}\n" f"Email: {email}\n\n" f"Message:\n{message_body}\n"
            )

            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    "Thank you for reaching out! Your message has been sent successfully.",
                )
            except Exception as e:
                messages.error(
                    request, f"An error occurred while sending your message: {str(e)}"
                )

            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact/contact.html", {"form": form})
