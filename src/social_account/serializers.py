import requests
import oauthlib
import oauthlib.oauth2
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SocialProvider, SocialAccount
from .exceptions import OauthException


User = get_user_model()


class OauthLoginSerializer(serializers.Serializer):

    provider = serializers.CharField()

    def validate(self, attrs):
        provider_name = attrs.pop("provider")
        request = self.context["request"]
        try:
            url = SocialProvider.objects.initalize_login(request, provider_name)
        except SocialProvider.DoesNotExist:
            raise serializers.ValidationError("%s is not a register provider" % provider_name)
        attrs["auth_url"] = url
        return attrs



class OauthCallbackSerialzier(serializers.Serializer):

    provider = serializers.CharField()
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True)
    error = serializers.CharField(required=False)

    def get_provider(self, provider):
        if hasattr(self, "_provider") and self._provider:
            return self._provider
        obj = SocialProvider.objects.get(provider=provider)
        self._provider = obj
        return obj

    def validate(self, attrs):
        request = self.context["request"]
        if (state := attrs["state"]) and state != request.session["state"]:
            raise OauthException()
        client = self.get_client()
        provider = self._provider
        token_body = client.prepare_request_body(
            code=attrs["code"],
            redirect_uri=provider.callback_url,
            client_id=provider.client_id,
            client_secret=provider.secret_key
        )
        print("\n", token_body)
        response = requests.post(provider.token_url, data=token_body)
        
        client.parse_request_body_response(response.text)
        header = self.get_header(client)
        
        profile_response = requests.get(provider.userinfo_url, headers=header)
        view = self.context["view"]
        social_account = view.create_user_social(request, profile_response.json())
        if social_account.user and not isinstance(social_account.user, User):
            raise OauthException()
        user = social_account.user
        token = RefreshToken.for_user(user)
        user_data = {
            "user_id": user.pk, 
            "access_token": token.access_token,
            "refresh_token": str(token),
            "social_account": SocialAccountSerializer(instance=social_account)
        }
        attrs["user"] = user_data
        return super().validate(attrs)
    
    def get_client(self):
        if hasattr(self, "_client") and self._client:
            return self._client
        obj = self.get_provider(self.validated_data["provider"])
        self._client = client = oauthlib.oauth2.WebApplicationClient(obj.client_id)
        return client
    

class SocialAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialAccount
        fields = (
            "provider",
        )