from rest_framework.views import APIView
from rest_framework.response import Response

from social_account.serializers import OauthCallbackSerialzier


class BaseOauthCallbackAPIView(APIView):
    """
    Base Oauth callback api view.
    """

    provider_name = None
    serializer_class = OauthCallbackSerialzier

    def get_serializer(self, request, *args, **kwargs):
        context = {"request": request, "view": self}
        return self.serializer_class(*args, context=context, **kwargs)

    def get(self, request, *args, **kwargs):
        query_dict = request.query_params.copy()
        query_dict["provider"] = self.provider_name
        serializer = self.get_serializer(request, data=query_dict)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)

    def create_user_social(self, request, attrs):
        return NotImplemented

