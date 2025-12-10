import secrets

import oauthlib
import oauthlib.oauth2
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured



class SocialProviderManager(models.Manager):

    def initalize_login(self, request, provider_name):

        provider = self.get(provider=provider_name)
        client = oauthlib.oauth2.WebApplicationClient(provider.client_id)
        # Set the oauth state
        provider.set_session_state(request)
        url = client.prepare_request_uri(
            provider.authorization_url,
            scope=provider.scope,
            state=request.session["state"]
        )
        return url



class SocialProvider(models.Model):

    provider = models.CharField(max_length=100, db_index=True)
    client_id = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "client_id", "secret_key"],
                name="social_provider_unique"
            )
        ]
    
    objects = SocialProviderManager()

    @property
    def scope(self):
        if hasattr(self, "_scope") and self._scope:
            return self._scope
        self._scope = scope = self.settings.get("SCOPE", [])
        return scope

    @property
    def settings(self):
        provider = self.get_provider()
        return settings.SOCIAL_PROVIDER[provider]

    def get_provider(self):
        if not self.provider:
            ImproperlyConfigured("Instance has not been saved.")
        return self.provider
    
    def set_session_state(self, request) -> None:
        request.session["state"] = secrets.token_urlsafe(16)


class SocialAccount(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="social_accounts",
        on_delete=models.CASCADE
    )
    access_token = models.CharField(max_length=200, default="")
    refresh_token = models.CharField(max_length=200, default="")
    provider = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    profile_url = models.URLField(default="")
    profile_data = models.JSONField()


    class Meta:
        unique_together = ["user", "provider"]