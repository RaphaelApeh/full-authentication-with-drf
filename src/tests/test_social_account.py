from unittest import mock

from rest_framework.test import APIRequestFactory

from .base import TestCase
from social_account.views.base import OauthLoginAPIView, BaseOauthCallbackAPIView
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


    def test_oauth_user_fetch_view(self):

        request = self.factory.get("/")
        request_mock = mock.MagicMock()
        client_mock = mock.MagicMock()
        request.session = {}
        request_mock.json.return_value = {
            "username": "johndoe", 
            "email": "johndoe@test.com"
        }
        client_mock.access_token.return_value = "token"
        request_mock.raise_for_status.return_value = None
        view = BaseOauthCallbackAPIView()
        view.request = request
        view.redirect_url="https://example.com/redirect",
        view.userinfo_url="https://example.com/user",
        view.token_url = "https://example.com/token"
        with mock.patch.object(view, "get_response", request_mock):
            data = view._fetch_userinfo(request, client_mock)
            self.assertIsNotNone(data)
            assert request.session["username"] == "johndoe"
        