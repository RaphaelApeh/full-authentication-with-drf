from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import SocialProvider, SocialAccount
from .exceptions import OauthException


User = get_user_model()


class OauthLoginSerializer(serializers.Serializer):

    provider = serializers.CharField()

    def validate(self, attrs):
        provider_name = attrs.pop("provider")
        try:
            SocialProvider.objects.get(provider_name)
        except SocialProvider.DoesNotExist:
            raise serializers.ValidationError("%s is not a register provider" % provider_name)
        return attrs



class OauthCallbackSerialzier(serializers.Serializer):

    provider = serializers.CharField()
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True)
    error = serializers.CharField(required=False)

    def validate(self, attrs):
        request = self.context["request"]
        if (state := attrs["state"]) and state != request.session["state"]:
            raise OauthException()
        del request.session["state"]
        error = attrs.get("error", "")
        if error:
            raise OauthException()
        return super().validate(attrs)
    
    

class SocialAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialAccount
        fields = (
            "provider",
        )