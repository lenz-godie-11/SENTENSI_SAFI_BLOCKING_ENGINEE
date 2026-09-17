


# ruff: noqa: N999

from django.apps import AppConfig


class BlockingConfig(AppConfig):
    # Uses Django's standard BigAutoField for automatically generated IDs.
    default_auto_field = "django.db.models.BigAutoField"

    # Points Django to the package containing the Blocking Engine app.
    name = "BlockingEngine.Blocking"