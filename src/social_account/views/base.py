from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login as auth_login
from django.core.exceptions import FieldDoesNotExist

from social_account.serializers import (
    OauthCallbackSerialzier,
    OauthLoginSerializer
)
from social_account.models import SocialAccount
from social_account.mixins import OauthClientMixin


User = get_user_model()


class OauthLoginAPIView(OauthClientMixin, APIView):

    authorization_url = None
    serializer_class = OauthLoginSerializer

    def get(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=dict(provider=self.provider_name))
        serializer.is_valid(raise_exception=True)
        
        client = self.get_client(serializer.validated_data["provider"])
        provider = self._provider #noqa
        state = provider.set_session_state(request)
        url = client.prepare_request_uri(
            self.authorization_url,
            scope=provider.scope,
            state=state
        )
        return Response(
            {"authentication_url": url}
        )

    def get_serializer(self, *args, **kwargs):
        context = {"request": self.request, "view": self}
        return self.serializer_class(*args, context=context, **kwargs)


class BaseOauthCallbackAPIView( 
    OauthClientMixin,
    APIView
    ):
    """
    Base Oauth callback api view.
    """

    token_url = None
    userinfo_url = None
    redirect_url = None
    header_type = "Bearer"
    serializer_class = OauthCallbackSerialzier
    authentication_classes = []

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
        user_dict = self._fetch_userinfo(request, client)

        social = self.create_user_social(request, client, user_dict)
        
        token = self.complete_login(request, social)
        return Response({
            "user_id": social.user_id,
            "social_id": social.pk,
            "provider": self.provider_name,
            "access_token": str(token.access_token),
            "refresh_token": str(token)
        }, status=status.HTTP_201_CREATED)
    
    def complete_login(self, request, social):
        self.login(request, social)

        token = RefreshToken.for_user(social.user)
        return token

    def create_user_social(self, request, client, user_dict):
        assert isinstance(user_dict, dict)
        username = user_dict["username"]
        user, _ = User.objects.get_or_create(username=username)
        profile_url = user_dict.pop("profile_url", "")
        user.set_unusable_password()
        for name in user_dict:
            try:
                user._meta.get_field(name)
                setattr(user, name, user_dict.pop(name))
            except FieldDoesNotExist:
                continue
        user.save()
        social_account = SocialAccount.objects.create(
            user=user,
            provider=self.provider_name,
            access_token=client.access_token,
            refresh_token=client.refresh_token,
            profile_url=profile_url,
            profile_data=request.session["profile_data"]
        )
        return social_account


    def _fetch_userinfo(self, request, client):
        headers = self._get_header(client.token["access_token"])
        response = self.get_response(self.userinfo_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        request.session["profile_data"] = data
        return data
    

    def _get_header(self, token):
        return {
            "Authorization": "%s %s" % (self.header_type, token)
        }

    def login(self, request, useraccount):
        user = useraccount.user
        auth_login(user)

    @property
    def setting(self):
        getattr(settings, "SOCIAL_PROVIDER", {}).get(self.provider_name, {})
    
    def get_redirect_url(self, request):
        if redirect_url := (self.settings.get("REDIRECT_URL") or self.redirect_url or settings.DEFAULT_CALLBACK_URL):
            return redirect_url
        view_url = reverse("%s_callback" % self.provider_name)
        return request.build_absolute_uri(view_url)
