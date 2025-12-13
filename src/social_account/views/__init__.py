from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_account.models import SocialAccount
from social_account.serializers import DisconnectSerializer


class DisconnectSocialAPIView(GenericAPIView):

    permission_classes = (IsAuthenticated,)
    model = SocialAccount
    serializer_class = DisconnectSerializer

    def get(self, request, social_id, *args, **kwargs):
        serializer = self.get_serializer(data={"social_id": social_id })
        serializer.is_valid(raise_exception=True)
        social = serializer.validated_data["social"]
        provider = social.provider
        try:
            social.revoke(request)
        except Exception as e:
            if revoke_url := getattr(e, "revoke_url"):
                print(f"revoke_url is {revoke_url:!r}")
            return Response("Cannot retrieve revoke url", status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(f"provider {provider} as successfully been revoke", status=status.HTTP_202_ACCEPTED)

