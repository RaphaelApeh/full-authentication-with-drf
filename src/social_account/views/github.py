from .base import BaseOauthCallbackAPIView


class GithubOauthCallbackAPIView(BaseOauthCallbackAPIView):

    provider_name = "github"
    header_type = "token"
    userinfo_url = "https://github.com/user"
    token_url = "https://github.com/login/oauth/access_token"


    def create_user_social(self, request, attrs):
        attrs.update(
            {
                "username": attrs["login"],
            }
        )
        return super().create_user_social(request, attrs)