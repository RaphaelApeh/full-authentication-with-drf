import requests
import oauthlib.oauth2
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model, login as auth_login
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist

from social_account.serializers import OauthCallbackSerialzier
from social_account.models import SocialProvider, SocialAccount


User = get_user_model()


class BaseOauthCallbackAPIView(APIView):
    """
    Base Oauth callback api view.
    """

    provider_name = None
    token_url = None
    userinfo_url = None
    header_type = "Bearer"
    serializer_class = OauthCallbackSerialzier

    def get_serializer(self, request, *args, **kwargs):
        context = {"request": request, "view": self}
        return self.serializer_class(*args, context=context, **kwargs)

    def get(self, request, *args, **kwargs):
        query_dict = request.query_params.copy()
        query_dict["provider"] = self.provider_name
        serializer = self.get_serializer(request, data=query_dict)
        serializer.is_valid(raise_exception=True)
        client = self.get_client()

        provider = self.get_provider()
        self._authenticate_client(
            request, 
            client=client,
            provider=provider,
            code=query_dict["code"]
        )
        attr = self._fetch_userinfo(request, client)

        social_user = self.create_user_social(request, attr)
        self.login(request, social_user)
        return Response(serializer.validated_data, status=200)

    def create_user_social(self, request, attrs):
        assert isinstance(attrs, dict)
        username = attrs["username"]
        user, _ = User.objects.get_or_create(username=username)
        password = attrs.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        for name in attrs:
            try:
                user._meta.get_field(name)
                setattr(user, name, attrs[name])
            except FieldDoesNotExist:
                pass
        user.save()
        social_account = SocialAccount.objects.create(
            user=user,
            provider=self.provider_name,
            profile_data=attrs
        )
        return social_account


    def _fetch_userinfo(self, request, client):
        headers = self._get_header(client.token["access_token"])
        response = requests.get(self.userinfo_url, headers=headers)
        response.raise_for_status()
        return response.json()
    

    def _get_header(self, token):
        return {
            "Authorization": "%s %s" % (self.header_type, token)
        }

    def login(self, request, useraccount):
        user = useraccount.user
        auth_login(user)

        
    
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


    def get_client(self):
        if hasattr(self, "_client") and self._client:
            return self._client
        obj = self.get_provider()
        self._client = client = oauthlib.oauth2.WebApplicationClient(obj.client_id)
        return client
    
    def get_redirect_url(self, request):
        url = reverse("%s_callback" % self.provider_name)
        return url

    def get_provider(self):
        if hasattr(self, "_provider") and self._provider:
            return self._provider
        if not (provider := self.provider_name):
            raise ImproperlyConfigured(
                f"{type(self).__name__}.provider_name must be set."
            )
        obj = SocialProvider.objects.get(provider=provider)
        self._provider = obj
        return obj