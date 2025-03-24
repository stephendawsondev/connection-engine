from django.apps import AppConfig
import os


class ContactConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    verbose_name = name.replace("_", " ").title()
