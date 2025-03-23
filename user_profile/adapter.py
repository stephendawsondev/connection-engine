from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user_type = form.cleaned_data.get("user_type")
        user._user_type = user_type
        if commit:
            user.save()
        return user

    def send_mail(self, template_prefix, email, context):
        subject = render_to_string(f"{template_prefix}_subject.txt", context)
        subject = " ".join(subject.splitlines()).strip()
        txt_body = render_to_string(f"{template_prefix}_message.txt", context)

        try:
            html_body = render_to_string(f"{template_prefix}_message.html", context)
        except:
            html_body = None

        from_email = settings.DEFAULT_FROM_EMAIL or "noreply@example.com"
        msg = EmailMultiAlternatives(subject, txt_body, from_email, [email])

        if html_body:
            msg.attach_alternative(html_body, "text/html")

        msg.send()
