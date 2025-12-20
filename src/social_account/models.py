import secrets

import requests
import oauthlib
import oauthlib.oauth2
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .exceptions import SocialInvokeError


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

class SocialSettingMixin:

    @property
    def setting(self):
        return getattr(settings, "SOCIAL_PROVIDER", {}).get(self.provider, {})


class SocialProvider(SocialSettingMixin, models.Model):

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
    def setting(self):
        social_provider = getattr(settings, "SOCIAL_PROVIDER", {})
        if not self.provider:
            return {}
        return social_provider.get(self.provider, {})

    @property
    def scope(self):
        if hasattr(self, "_scope") and self._scope:
            return self._scope
        self._scope = scope = self.setting.get("SCOPE", [])
        return scope

    def get_provider(self):
        if not self.provider:
            ImproperlyConfigured("Instance has not been saved.")
        return self.provider
    
    def set_session_state(self, request) -> None:
        auth = SocialAuth.objects.create()
        return auth.state


class SocialAuth(models.Model):

    code = models.CharField(max_length=100, default="", db_index=True)
    state = models.CharField(
        max_length=100, 
        default=secrets.token_urlsafe(16)
    )
    expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if code := self.code:
            return code
        return self.state


class SocialAccount(SocialSettingMixin, models.Model):

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


    def revoke(self, request, rovoke_url=None) -> None:
        
        revoke_url = rovoke_url or self.setting.get("REVOKE_URL")
        if not revoke_url:
            raise SocialInvokeError(revoke_url, "revoke url was not set.")
        if not self.access_token:
            raise ImproperlyConfigured(
                f"SocialAccount({self.user}, {self.provider}).access_token is None"
            )
        response = requests.post(
            revoke_url, 
            data={"token": self.access_token},
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        self.delete()
