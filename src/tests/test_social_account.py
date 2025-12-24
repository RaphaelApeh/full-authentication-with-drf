from unittest import mock

from rest_framework.test import APIRequestFactory

from .base import TestCase
from social_account.views.base import OauthLoginAPIView
from social_account.models import SocialProvider


class SocailTestCase(TestCase):


    def setUp(self):
        self.factory = APIRequestFactory()
        return super().setUp()

    def test_oauth_auth_view(self):
        SocialProvider.objects.create(
            provider="example",
            client_id="abc",
            secret_key="hello"
        )
        request = self.factory.get("/")
        view = OauthLoginAPIView.as_view(
            authorization_url="https://example.com/authorize",
            provider_name="example"
        )
        response = view(request)
        self.assertStatusCode(response)
        assert "https://example.com/authorize?response_type=code&client_id=abc" in response.data["authentication_url"]