from rest_framework import serializers

from .models import SocialProvider



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

