import os

from django.apps import AppConfig


class DonationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    verbose_name = name.replace("_", " ").title()

    def ready(self):
        import donations.signals
