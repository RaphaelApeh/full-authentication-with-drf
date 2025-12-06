import requests
import oauthlib.oauth2
from django.core.exceptions import ImproperlyConfigured

from .models import SocialProvider


class OauthProviderMixin:

    provider_name = None


    def get_provider(self, provider=None):
        if hasattr(self, "_provider") and self._provider:
            return self._provider
        if not (_provider := provider or getattr(self, "provider_name", None)):
            raise ImproperlyConfigured(
                f"{type(self).__name__}.provider_name must be set."
            )
        obj = SocialProvider.objects.get(provider=_provider)
        self._provider = obj
        return obj
    

class OauthClientMixin:

    
    def get_client(self):
        if hasattr(self, "_client") and self._client:
            return self._client
        obj = self.get_provider()
        self._client = client = oauthlib.oauth2.WebApplicationClient(obj.client_id)
        return client
        
    def _authenticate_client(self, request, code, client, provider):

        token_body = client.prepare_request_body(
            code=code,
            redirect_uri=self.get_redirect_url(request),
            client_id=provider.client_id,
            client_secret=provider.secret_key
        )
        
        print("\n", token_body)
        response = requests.post(self.token_url, data=token_body)
        response.raise_for_status()
        client.parse_request_body_response(response.text)
