from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import SocialProvider, SocialAccount, SocialAuth
from .exceptions import OauthException

User = get_user_model()


class OauthLoginSerializer(serializers.Serializer):

    provider = serializers.CharField()

    def validate(self, attrs):
        provider_name = attrs.get("provider")
        try:
            SocialProvider.objects.get(provider=provider_name)
        except SocialProvider.DoesNotExist:
            raise serializers.ValidationError("%s is not a register provider" % provider_name)
        return attrs



class OauthCallbackSerialzier(serializers.Serializer):

    provider = serializers.CharField()
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True)
    error = serializers.CharField(required=False)

    def validate(self, attrs):
        state = attrs["state"]
        
        try:
            obj = SocialAuth.objects.get(state=state)
        except SocialAuth.DoesNotExist:
            raise serializers.ValidationError("")
        obj.expired = False
        obj.save()
        error = attrs.get("error", "")
        if error:
            raise OauthException()
        return super().validate(attrs)
    
    

class SocialAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialAccount
        fields = (
            "provider",
            "profile_url",
            "timestamp",
            ""
        )

class DisconnectSerializer(serializers.Serializer):

    social_id = serializers.ReadOnlyField()

    def validate(self, attrs):
        social_id = attrs["social_id"]
        try:
            social = SocialAccount.objects.get(pk=social_id)
            attrs["social"] = social
        except SocialAccount.DoesNotExist as e:
            attrs["social"] = None
            raise serializers.ValidationError(str(e))
        if not attrs["social"]:
            raise serializers.ValidationError("Invalid social account.")
        return super().validate(attrs)