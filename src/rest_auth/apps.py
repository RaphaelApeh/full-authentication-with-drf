from django.apps import AppConfig


class RestAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rest_auth"

    def ready(self):
        from . import signals