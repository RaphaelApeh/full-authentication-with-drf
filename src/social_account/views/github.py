from django.conf import settings

from .base import BaseOauthCallbackAPIView, OauthLoginAPIView



class GithubLoginAPIView(OauthLoginAPIView):

    authorization_url = (
        getattr(settings, "SOCIAL_PROVIDER", {}).get("github", {}).get("AUTH_URL", "https://github.com/login/oauth/authorize")
    )
    provider_name = "github"


class GithubOauthCallbackView(BaseOauthCallbackAPIView):

    provider_name = "github"
    header_type = "token"
    userinfo_url = (
        getattr(settings, "SOCIAL_PROVIDER", {}).get("USER_INFO_URL", "https://github.com/user")
    )
    token_url = (
        getattr(settings, "SOCIAL_PROVIDER", {}).get("TOKEN_URL", "https://github.com/login/oauth/access_token")
    )


    def create_user_social(self, request, attrs):
        attrs.update(
            {
                "username": attrs["login"],
                "profile_url": attrs.get("avatar_url"),
            }
        )
        return super().create_user_social(request, attrs)