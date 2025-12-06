import requests
import oauthlib.oauth2
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model, login as auth_login
from django.core.exceptions import FieldDoesNotExist

from social_account.serializers import (
    OauthCallbackSerialzier,
    OauthLoginSerializer
)
from social_account.models import SocialAccount
from social_account.mixins import (
    OauthProviderMixin,
    OauthClientMixin
)


User = get_user_model()


class OauthLoginAPIView(OauthProviderMixin, APIView):

    serializer_class = OauthLoginSerializer

    def get(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        provider = self.get_provider(serializer.validated_data["provider"])
        client = oauthlib.oauth2.WebApplicationClient(provider.client_id)
        provider.set_session_state(request)
        url = client.prepare_request_uri(
            provider.authorization_url,
            scope=provider.scope,
            state=request.session["state"]
        )
        return Response(
            {"authentication_url": url}
        )

    def get_serializer(self, *args, **kwargs):
        context = {"request": self.request, "view": self}
        return self.serializer_class(*args, context=context, **kwargs)


class BaseOauthCallbackAPIView(
    OauthProviderMixin, 
    OauthClientMixin,
    APIView
    ):
    """
    Base Oauth callback api view.
    """

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
                continue
        user.save()
        request.session["profile_data"] = attrs
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

    
    def get_redirect_url(self, request):
        view_url = reverse("%s_callback" % self.provider_name)
        return request.build_absolute_uri(view_url)
